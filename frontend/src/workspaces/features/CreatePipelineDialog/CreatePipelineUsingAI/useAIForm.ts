import { useTranslation } from "next-i18next";
import { useRouter } from "next/router";
import { useState } from "react";
import { CreatePipelineDialog_WorkspaceFragment } from "../CreatePipelineDialog.generated";
import {
  useCreateAssistantConversationMutation,
  useSendAssistantMessageMutation,
} from "assistant/graphql/mutations.generated";

export type AIFormInstance = {
  prompt: string;
  setPrompt: (value: string) => void;
  handleSubmit: () => void;
  isSubmitting: boolean;
  error: string | null;
  reset: () => void;
};

export function useAIForm(
  workspace: CreatePipelineDialog_WorkspaceFragment,
): AIFormInstance {
  const { t } = useTranslation();
  const router = useRouter();
  const [prompt, setPrompt] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const [createConversation] = useCreateAssistantConversationMutation();
  const [sendMessage] = useSendAssistantMessageMutation();

  const reset = () => {
    setPrompt("");
    setError(null);
  };

  const handleSubmit = async () => {
    if (!prompt.trim()) return;
    setIsSubmitting(true);
    setError(null);
    try {
      const convResult = await createConversation({
        variables: {
          input: { workspaceSlug: workspace.slug, instructionSet: "pipeline" },
        },
      });
      const conversationId =
        convResult.data?.createAssistantConversation.conversation?.id;
      if (!conversationId) {
        setError(t("Failed to start AI conversation."));
        return;
      }

      const msgResult = await sendMessage({
        variables: { input: { conversationId, message: prompt } },
      });

      const message = msgResult.data?.sendAssistantMessage.message;
      const createInvocation = message?.toolInvocations?.find(
        (inv) => inv.toolName === "create_pipeline" && inv.success,
      );

      if (createInvocation?.toolOutput) {
        const output = createInvocation.toolOutput as any;
        const pipelineCode = output?.pipeline?.code;
        if (pipelineCode) {
          await router.push(
            `/workspaces/${encodeURIComponent(
              router.query.workspaceSlug as string,
            )}/pipelines/${encodeURIComponent(pipelineCode)}/code`,
          );
          return;
        }
      }

      setError(
        message?.content ||
          t("The AI could not create the pipeline. Please try again."),
      );
    } catch {
      setError(t("An error occurred while creating the pipeline."));
    } finally {
      setIsSubmitting(false);
    }
  };

  return { prompt, setPrompt, handleSubmit, isSubmitting, error, reset };
}

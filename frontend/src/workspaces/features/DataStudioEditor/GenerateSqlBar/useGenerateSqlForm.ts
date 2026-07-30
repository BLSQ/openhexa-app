import { useTranslation } from "next-i18next";
import { useCallback, useEffect, useRef, useState } from "react";
import { getErrorCodeMessage } from "assistant/helpers";
import { InstructionSet } from "assistant/instructions";
import { getPublicEnv } from "core/helpers/runtimeConfig";
import useStreamingFetch from "core/hooks/useStreamingFetch";
import { useCreateAssistantConversationMutation } from "assistant/graphql/mutations.generated";

export enum GenerateSqlPhase {
  Idle = "idle",
  Generating = "generating",
  Done = "done",
  Error = "error",
}

export type GenerateSqlFormInstance = {
  prompt: string;
  setPrompt: (value: string) => void;
  handleSubmit: () => void;
  cancel: () => void;
  phase: GenerateSqlPhase;
  error: string | null;
  reset: () => void;
};

function getStreamUrl(conversationId: string): string {
  const apiBasePath =
    process.env.NEXT_PUBLIC_API_BASE_PATH ||
    getPublicEnv().OPENHEXA_BACKEND_URL;
  return `${apiBasePath}/assistant/conversations/${conversationId}/stream/`;
}

// The generate-SQL agent has no user-facing tool step: its validated final
// answer is the query itself, delivered as `output` on the `done` event (see
// GenerateSqlAgent._final_output on the backend). So unlike useAIForm (which
// tracks a tool_call/tool_result to know when the pipeline was created), this
// hook only needs to wait for `done` and read `output` off it. It still mirrors
// useAIForm's brief Done pause (via closeTimerRef) before calling onGenerated,
// so the bar doesn't vanish the instant streaming ends.
export function useGenerateSqlForm(
  workspaceSlug: string,
  onGenerated: (sql: string) => void,
): GenerateSqlFormInstance {
  const { t } = useTranslation();
  const [prompt, setPrompt] = useState("");
  const [phase, setPhase] = useState<GenerateSqlPhase>(GenerateSqlPhase.Idle);
  const [error, setError] = useState<string | null>(null);
  const onGeneratedRef = useRef(onGenerated);
  onGeneratedRef.current = onGenerated;
  const closeTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  const [createConversation] = useCreateAssistantConversationMutation();

  const clearCloseTimer = useCallback(() => {
    if (closeTimerRef.current !== null) {
      clearTimeout(closeTimerRef.current);
      closeTimerRef.current = null;
    }
  }, []);

  const { send, abort, streamError } = useStreamingFetch({
    done: (data) => {
      const { output } = (data ?? {}) as { output?: string | null };
      if (output) {
        setPhase(GenerateSqlPhase.Done);
        closeTimerRef.current = setTimeout(() => {
          onGeneratedRef.current(output);
        }, 500);
      } else {
        setPhase(GenerateSqlPhase.Error);
        setError(t("The AI could not generate a query. Please try again."));
      }
    },
    error: (data) => {
      const { error_code } = (data ?? {}) as { error_code?: string };
      setPhase(GenerateSqlPhase.Error);
      setError(getErrorCodeMessage(t, error_code));
    },
  });

  useEffect(() => {
    if (streamError) {
      setPhase(GenerateSqlPhase.Error);
      setError(
        t(
          "Could not connect to the server. Please check your connection and try again.",
        ),
      );
    }
  }, [streamError, t]);

  useEffect(() => clearCloseTimer, [clearCloseTimer]);

  const reset = useCallback(() => {
    clearCloseTimer();
    setPrompt("");
    setError(null);
    setPhase(GenerateSqlPhase.Idle);
  }, [clearCloseTimer]);

  const cancel = useCallback(() => {
    clearCloseTimer();
    abort();
    setError(null);
    setPhase(GenerateSqlPhase.Idle);
  }, [abort, clearCloseTimer]);

  const handleSubmit = useCallback(async () => {
    if (!prompt.trim() || phase === GenerateSqlPhase.Generating) return;
    clearCloseTimer();
    setError(null);
    setPhase(GenerateSqlPhase.Generating);
    try {
      const convResult = await createConversation({
        variables: {
          input: { workspaceSlug, instructionSet: InstructionSet.GENERATE_SQL },
        },
      });
      const conversationId =
        convResult.data?.createAssistantConversation.conversation?.id;
      if (!conversationId) {
        setPhase(GenerateSqlPhase.Error);
        setError(t("Failed to start AI conversation."));
        return;
      }
      await send(getStreamUrl(conversationId), { message: prompt });
    } catch {
      setPhase(GenerateSqlPhase.Error);
      setError(t("An error occurred while generating the query."));
    }
  }, [
    prompt,
    phase,
    clearCloseTimer,
    createConversation,
    workspaceSlug,
    send,
    t,
  ]);

  return { prompt, setPrompt, handleSubmit, cancel, phase, error, reset };
}

import { useCallback, useRef, useState } from "react";
import ChatPane from "assistant/features/ChatPane";
import { useCreateAssistantConversationMutation } from "assistant/graphql/mutations.generated";
import { AssistantConversationMessagesQuery } from "assistant/graphql/queries.generated";
import { LinkedObjectType } from "graphql/types";
import { ProposedFile } from "workspaces/features/FilesEditor/FilesEditor";

type Message = NonNullable<
  AssistantConversationMessagesQuery["assistantConversation"]
>["messages"]["items"][0];

type Props = {
  pipelineId: string;
  workspaceSlug: string;
  monthlyLimitExceeded: boolean;
  onProposedFiles: (files: ProposedFile[] | null) => void;
};

export default function PipelineEditChatPanel({
  pipelineId,
  workspaceSlug,
  monthlyLimitExceeded,
  onProposedFiles,
}: Props) {
  const conversationIdRef = useRef<string | null>(null);
  const [conversationName, setConversationName] = useState<string | null>(null);

  const [createConversation] = useCreateAssistantConversationMutation();

  const handleCreateConversation = useCallback(async () => {
    const result = await createConversation({
      variables: {
        input: {
          workspaceSlug,
          linkedObjectId: pipelineId,
          linkedObjectType: LinkedObjectType.Pipeline,
        },
      },
    });
    const id = result.data?.createAssistantConversation?.conversation?.id ?? null;
    conversationIdRef.current = id;
    return id;
  }, [createConversation, workspaceSlug, pipelineId]);

  const handleMessagesChange = useCallback(
    (messages: Message[]) => {
      // Find the most recent propose_pipeline_version call across all assistant messages
      for (let i = messages.length - 1; i >= 0; i--) {
        const msg = messages[i];
        if (msg.role !== "assistant") continue;
        const proposal = msg.toolInvocations.find(
          (t: Message["toolInvocations"][0]) =>
            t.toolName === "propose_pipeline_version" && t.success,
        );
        if (proposal?.toolOutput) {
          const files = (proposal.toolOutput as { files: ProposedFile[] })?.files;
          if (Array.isArray(files)) {
            onProposedFiles(files);
            return;
          }
        }
      }
      onProposedFiles(null);
    },
    [onProposedFiles],
  );

  return (
    <div className="flex flex-col h-full border rounded-lg overflow-hidden bg-white">
      <div className="shrink-0 border-b border-gray-200 px-4 py-3">
        <h3 className="text-sm font-medium text-gray-700">AI Assistant</h3>
        <div className="text-xs mt-1 text-gray-500">{conversationName ?? <span className="invisible">&nbsp;</span>}</div>
      </div>
      <div className="flex-1 min-h-0">
        <ChatPane
          conversationId={conversationIdRef.current}
          monthlyLimitExceeded={monthlyLimitExceeded}
          createConversation={handleCreateConversation}
          onConversationNameChange={setConversationName}
          onMessagesChange={handleMessagesChange}
        />
      </div>
    </div>
  );
}

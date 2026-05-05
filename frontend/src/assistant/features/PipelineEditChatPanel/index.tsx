import { useCallback, useEffect, useState } from "react";
import ChatPane from "assistant/features/ChatPane";
import ConversationList from "assistant/features/ConversationList";
import useTypewriter from "core/hooks/useTypewriter";
import { useCreateAssistantConversationMutation } from "assistant/graphql/mutations.generated";
import { AssistantConversationMessagesQuery } from "assistant/graphql/queries.generated";
import { LinkedObjectType } from "graphql/types";
import { ProposedFile } from "workspaces/features/FilesEditor/FilesEditor";

type Message = NonNullable<
  AssistantConversationMessagesQuery["assistantConversation"]
>["messages"]["items"][0];

export type PipelineConversation = {
  id: string;
  name?: string | null;
  createdAt: string;
};

type Props = {
  pipelineId: string;
  workspaceSlug: string;
  monthlyLimitExceeded: boolean;
  onProposedFiles: (files: ProposedFile[] | null) => void;
  conversations: PipelineConversation[];
  activeConversationId: string | null;
  onConversationChange: (id: string) => void;
  onConversationCreated: (conversation: PipelineConversation) => void;
  onConversationNameChange: (id: string, name: string) => void;
};

export default function PipelineEditChatPanel({
  pipelineId,
  workspaceSlug,
  monthlyLimitExceeded,
  onProposedFiles,
  conversations,
  activeConversationId,
  onConversationChange,
  onConversationCreated,
  onConversationNameChange,
}: Props) {
  const [conversationName, setConversationName] = useState<string | null>(null);
  const displayedConversationName = useTypewriter(conversationName);

  useEffect(() => {
    setConversationName(null);
  }, [activeConversationId]);

  const [createConversation, { loading: creating }] =
    useCreateAssistantConversationMutation();

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
    const conversation =
      result.data?.createAssistantConversation?.conversation ?? null;
    if (!conversation) return null;
    const newConv: PipelineConversation = {
      id: conversation.id,
      name: null,
      createdAt: conversation.createdAt,
    };
    onConversationCreated(newConv);
    return conversation.id;
  }, [createConversation, workspaceSlug, pipelineId, onConversationCreated]);

  const handleConversationNameChange = useCallback(
    (name: string) => {
      setConversationName(name);
      if (activeConversationId) {
        onConversationNameChange(activeConversationId, name);
      }
    },
    [activeConversationId, onConversationNameChange],
  );

  const handleToolResult = useCallback(
    (toolName: string, output: unknown, success: boolean) => {
      if (toolName !== "propose_pipeline_version" || !success) return;
      const files = (output as { files?: ProposedFile[] })?.files;
      if (Array.isArray(files)) {
        onProposedFiles(files);
      }
    },
    [onProposedFiles],
  );

  const handleMessagesChange = useCallback(
    (messages: Message[]) => {
      for (let i = messages.length - 1; i >= 0; i--) {
        const msg = messages[i];
        if (msg.role !== "assistant") continue;
        const proposal = msg.toolInvocations.find(
          (t: Message["toolInvocations"][0]) =>
            t.toolName === "propose_pipeline_version" && t.success,
        );
        if (proposal?.toolOutput) {
          const files = (proposal.toolOutput as { files: ProposedFile[] })
            ?.files;
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
    <div className="flex h-full border rounded-lg overflow-hidden bg-white">
      <ConversationList
        conversations={conversations}
        selectedId={activeConversationId}
        onSelect={onConversationChange}
        onNew={handleCreateConversation}
        creating={creating}
        className="w-48"
      />
      <div className="flex flex-col flex-1 min-w-0">
        <div className="shrink-0 border-b border-gray-200 px-4 py-3">
          <h3 className="text-sm font-medium text-gray-700">AI Assistant</h3>
          <div className="text-xs mt-1 text-gray-500">
            {displayedConversationName ??
              conversations.find((c) => c.id === activeConversationId)?.name ?? (
                <span className="invisible">&nbsp;</span>
              )}
          </div>
        </div>
        <div className="flex-1 min-h-0">
          <ChatPane
            conversationId={activeConversationId}
            monthlyLimitExceeded={monthlyLimitExceeded}
            createConversation={
              activeConversationId ? undefined : handleCreateConversation
            }
            onConversationNameChange={handleConversationNameChange}
            onToolResult={handleToolResult}
            onMessagesChange={handleMessagesChange}
          />
        </div>
      </div>
    </div>
  );
}

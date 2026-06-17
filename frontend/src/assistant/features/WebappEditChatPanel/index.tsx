import { useCallback, useEffect, useState } from "react";
import ChatPane from "assistant/features/ChatPane";
import useTypewriter from "core/hooks/useTypewriter";
import { useTranslation } from "next-i18next";
import { useCreateAssistantConversationMutation } from "assistant/graphql/mutations.generated";
import { AssistantConversationMessagesQuery } from "assistant/graphql/queries.generated";
import { LinkedObjectType } from "graphql/types";
import { PlusIcon } from "@heroicons/react/24/outline";
import clsx from "clsx";
import Time from "core/components/Time/Time";

type Message = NonNullable<
  AssistantConversationMessagesQuery["assistantConversation"]
>["messages"]["items"][0];

type ToolSegment = Extract<
  Message["content"][0],
  { __typename?: "AssistantToolSegment" }
>;

export type WebappProposedFile = { path: string; content: string };

export type WebappConversation = {
  id: string;
  name?: string | null;
  createdAt: string;
  updatedAt: string;
};

type Props = {
  webappId: string;
  workspaceSlug: string;
  monthlyLimitExceeded: boolean;
  onProposedFiles: (
    files: WebappProposedFile[] | null,
    toolInvocationId?: string,
  ) => void;
  conversations: WebappConversation[];
  activeConversationId: string | null;
  onConversationChange: (id: string) => void;
  onNewConversation: () => void;
  onConversationCreated: (conversation: WebappConversation) => void;
  onConversationNameChange: (id: string, name: string) => void;
};

export default function WebappEditChatPanel({
  webappId,
  workspaceSlug,
  monthlyLimitExceeded,
  onProposedFiles,
  conversations,
  activeConversationId,
  onConversationChange,
  onNewConversation,
  onConversationCreated,
  onConversationNameChange,
}: Props) {
  const { t } = useTranslation();
  const [conversationName, setConversationName] = useState<string | null>(null);
  const displayedConversationName = useTypewriter(conversationName);
  const [showHistory, setShowHistory] = useState(false);

  useEffect(() => {
    setConversationName(null);
    setShowHistory(false);
  }, [activeConversationId]);

  const [createConversation] = useCreateAssistantConversationMutation();

  const handleCreateConversation = useCallback(async () => {
    const result = await createConversation({
      variables: {
        input: {
          workspaceSlug,
          linkedObjectId: webappId,
          linkedObjectType: LinkedObjectType.StaticWebapp,
        },
      },
    });
    const conversation =
      result.data?.createAssistantConversation?.conversation ?? null;
    if (!conversation) return null;
    const newConv: WebappConversation = {
      id: conversation.id,
      name: null,
      createdAt: conversation.createdAt,
      updatedAt: conversation.updatedAt,
    };
    onConversationCreated(newConv);
    return conversation.id;
  }, [createConversation, workspaceSlug, webappId, onConversationCreated]);

  const handleConversationNameChange = useCallback(
    (name: string) => {
      setConversationName(name);
      if (activeConversationId) {
        onConversationNameChange(activeConversationId, name);
      }
    },
    [activeConversationId, onConversationNameChange],
  );

  const handleConversationNameLoaded = useCallback(
    (name: string) => {
      if (activeConversationId) {
        onConversationNameChange(activeConversationId, name);
      }
    },
    [activeConversationId, onConversationNameChange],
  );

  const handleToolResult = useCallback(
    (toolName: string, output: unknown, success: boolean) => {
      if (toolName !== "propose_webapp_changes" || !success) return;
      const files = (output as { files?: WebappProposedFile[] })?.files;
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
        const proposal = msg.content.find(
          (seg): seg is ToolSegment =>
            seg.__typename === "AssistantToolSegment" &&
            (seg as ToolSegment).toolName === "propose_webapp_changes" &&
            (seg as ToolSegment).success &&
            (seg as ToolSegment).proposalPending,
        ) as ToolSegment | undefined;
        if (proposal?.toolOutput) {
          const files = (proposal.toolOutput as { files: WebappProposedFile[] })
            ?.files;
          if (Array.isArray(files)) {
            onProposedFiles(files, proposal.id ?? undefined);
            return;
          }
        }
      }
    },
    [onProposedFiles],
  );

  return (
    <div className="flex flex-col h-full border rounded-lg overflow-hidden bg-white">
      <div className="shrink-0 border-b border-gray-200 px-4 py-3 flex items-start justify-between">
        <div className="min-w-0 flex-1">
          <h3 className="text-sm font-medium text-gray-700">AI Assistant</h3>
          {!showHistory && (
            <div className="text-xs mt-1 text-gray-500">
              {displayedConversationName ??
                conversations.find((c) => c.id === activeConversationId)
                  ?.name ?? <span className="invisible">&nbsp;</span>}
            </div>
          )}
        </div>
        <div className="flex items-center gap-2 shrink-0 ml-2 mt-0.5">
          {conversations.length > 0 && (
            <button
              onClick={() => setShowHistory((v) => !v)}
              className={clsx(
                "text-xs font-medium py-1 px-1.5 rounded transition-colors",
                showHistory
                  ? "bg-blue-50 text-blue-700"
                  : "text-gray-500 hover:text-gray-700 hover:bg-gray-100",
              )}
            >
              {t("History")}
            </button>
          )}
          <button
            onClick={onNewConversation}
            disabled={!activeConversationId}
            className="p-1 rounded hover:bg-gray-100 text-gray-500 hover:text-gray-700 disabled:opacity-50 disabled:cursor-not-allowed"
            title={t("New conversation")}
          >
            <PlusIcon className="h-4 w-4" />
          </button>
        </div>
      </div>

      {showHistory ? (
        <div className="flex-1 overflow-y-auto">
          {conversations.map((conv) => (
            <button
              key={conv.id}
              onClick={() => {
                onConversationChange(conv.id);
                setShowHistory(false);
              }}
              className={clsx(
                "w-full px-4 py-3 text-left text-sm border-b border-gray-100 transition-colors hover:bg-gray-50",
                activeConversationId === conv.id
                  ? "bg-blue-50 text-blue-700 font-medium"
                  : "text-gray-700",
              )}
            >
              <div className="flex items-center justify-between gap-2">
                <span className="truncate">
                  {conv.name || t("New conversation")}
                </span>
                <span className="shrink-0 text-xs text-gray-400">
                  <Time datetime={conv.updatedAt} />
                </span>
              </div>
            </button>
          ))}
        </div>
      ) : (
        <div className="flex-1 min-h-0">
          <ChatPane
            conversationId={activeConversationId}
            monthlyLimitExceeded={monthlyLimitExceeded}
            createConversation={
              activeConversationId ? undefined : handleCreateConversation
            }
            onConversationNameChange={handleConversationNameChange}
            onConversationNameLoaded={handleConversationNameLoaded}
            onToolResult={handleToolResult}
            onMessagesChange={handleMessagesChange}
          />
        </div>
      )}
    </div>
  );
}

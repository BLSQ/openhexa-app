import { gql, useMutation, useQuery } from "@apollo/client";
import { PaperAirplaneIcon } from "@heroicons/react/24/outline";
import clsx from "clsx";
import Spinner from "core/components/Spinner";
import { useTranslation } from "next-i18next";
import { FormEvent, useCallback, useEffect, useRef, useState } from "react";
import Markdown from "react-markdown";
import remarkGfm from "remark-gfm";

const SEND_MESSAGE_MUTATION = gql`
  mutation SendAssistantMessage($input: SendAssistantMessageInput!) {
    sendAssistantMessage(input: $input) {
      success
      errors
      message {
        id
        role
        content
        createdAt
      }
      usage {
        inputTokens
        outputTokens
        cost
      }
    }
  }
`;

const WORKSPACE_CONVERSATIONS_QUERY = gql`
  query WorkspaceAssistantConversations($workspaceSlug: String!) {
    workspace(slug: $workspaceSlug) {
      slug
      assistantConversations {
        id
        createdAt
        updatedAt
        messages {
          id
          role
          content
          createdAt
        }
        estimatedCost
      }
    }
  }
`;

const DELETE_CONVERSATION_MUTATION = gql`
  mutation DeleteAssistantConversation(
    $input: DeleteAssistantConversationInput!
  ) {
    deleteAssistantConversation(input: $input) {
      success
      errors
    }
  }
`;

type Message = {
  id: string;
  role: string;
  content: string;
  createdAt: string;
};

type Conversation = {
  id: string;
  createdAt: string;
  updatedAt: string;
  messages: Message[];
  estimatedCost: number;
};

type AssistantChatProps = {
  workspaceSlug: string;
};

const AssistantChat = ({ workspaceSlug }: AssistantChatProps) => {
  const { t } = useTranslation();
  const [input, setInput] = useState("");
  const [selectedConversationId, setSelectedConversationId] = useState<
    string | null
  >(null);
  const [pendingMessages, setPendingMessages] = useState<Message[]>([]);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const { data, refetch } = useQuery(WORKSPACE_CONVERSATIONS_QUERY, {
    variables: { workspaceSlug },
  });

  const [sendMessage, { loading: sending }] = useMutation(
    SEND_MESSAGE_MUTATION,
  );
  const [deleteConversation] = useMutation(DELETE_CONVERSATION_MUTATION);

  const conversations: Conversation[] =
    data?.workspace?.assistantConversations ?? [];
  const selectedConversation = conversations.find(
    (c) => c.id === selectedConversationId,
  );
  const displayMessages = [
    ...(selectedConversation?.messages ?? []),
    ...pendingMessages,
  ];

  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [displayMessages.length, scrollToBottom]);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    const message = input.trim();
    if (!message || sending) return;

    setInput("");

    const userMsg: Message = {
      id: `pending-${Date.now()}`,
      role: "user",
      content: message,
      createdAt: new Date().toISOString(),
    };
    setPendingMessages((prev) => [...prev, userMsg]);

    try {
      const { data: result } = await sendMessage({
        variables: {
          input: {
            workspaceSlug,
            conversationId: selectedConversationId,
            message,
          },
        },
      });

      if (result?.sendAssistantMessage?.success) {
        const { data: refreshed } = await refetch();
        setPendingMessages([]);

        if (!selectedConversationId && refreshed?.workspace) {
          const convos = refreshed.workspace.assistantConversations;
          if (convos.length > 0) {
            setSelectedConversationId(convos[0].id);
          }
        }
      } else {
        setPendingMessages((prev) => [
          ...prev,
          {
            id: `error-${Date.now()}`,
            role: "assistant",
            content: t(
              "An error occurred while processing your message. Please try again.",
            ),
            createdAt: new Date().toISOString(),
          },
        ]);
      }
    } catch {
      setPendingMessages((prev) => [
        ...prev,
        {
          id: `error-${Date.now()}`,
          role: "assistant",
          content: t("Failed to send message. Please try again."),
          createdAt: new Date().toISOString(),
        },
      ]);
    }
  };

  const handleNewConversation = () => {
    setSelectedConversationId(null);
    setPendingMessages([]);
  };

  const handleDeleteConversation = async (id: string) => {
    await deleteConversation({
      variables: { input: { id } },
    });
    if (selectedConversationId === id) {
      setSelectedConversationId(null);
      setPendingMessages([]);
    }
    await refetch();
  };

  return (
    <div className="flex h-[calc(100vh-12rem)] gap-4">
      {/* Conversation sidebar */}
      <div className="flex w-64 shrink-0 flex-col rounded-lg bg-white shadow-sm">
        <div className="border-b p-3">
          <button
            onClick={handleNewConversation}
            className="w-full rounded-md bg-blue-600 px-3 py-2 text-sm font-medium text-white hover:bg-blue-700"
          >
            {t("New conversation")}
          </button>
        </div>
        <div className="flex-1 overflow-y-auto">
          {conversations.map((conv) => (
            <div
              key={conv.id}
              className={`group flex cursor-pointer items-center justify-between border-b px-3 py-2 text-sm hover:bg-gray-50 ${
                selectedConversationId === conv.id ? "bg-blue-50" : ""
              }`}
              onClick={() => {
                setSelectedConversationId(conv.id);
                setPendingMessages([]);
              }}
            >
              <div className="min-w-0 flex-1">
                <div className="truncate text-gray-700">
                  {conv.messages[0]?.content.substring(0, 40) ||
                    t("Empty conversation")}
                  ...
                </div>
                <div className="text-xs text-gray-400">
                  {new Date(conv.updatedAt).toLocaleDateString()}
                </div>
              </div>
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  handleDeleteConversation(conv.id);
                }}
                className="ml-2 hidden text-xs text-red-400 hover:text-red-600 group-hover:block"
              >
                {t("Delete")}
              </button>
            </div>
          ))}
          {conversations.length === 0 && (
            <div className="p-4 text-center text-sm text-gray-400">
              {t("No conversations yet")}
            </div>
          )}
        </div>
      </div>

      {/* Chat area */}
      <div className="flex flex-1 flex-col rounded-lg bg-white shadow-sm">
        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-4">
          {displayMessages.length === 0 && (
            <div className="flex h-full items-center justify-center">
              <div className="text-center text-gray-400">
                <p className="text-lg font-medium">
                  {t("OpenHEXA Assistant")}
                </p>
                <p className="mt-1 text-sm">
                  {t(
                    "Ask questions about your data, explore files, or query your database.",
                  )}
                </p>
              </div>
            </div>
          )}
          {displayMessages.map((msg) => (
            <div
              key={msg.id}
              className={`mb-4 flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
            >
              <div
                className={clsx(
                  "max-w-[75%] rounded-lg px-4 py-2",
                  msg.role === "user"
                    ? "bg-blue-600 text-white"
                    : "bg-gray-100 text-gray-800",
                )}
              >
                {msg.role === "user" ? (
                  <p className="whitespace-pre-wrap text-sm">{msg.content}</p>
                ) : (
                  <div className="prose prose-sm max-w-none prose-headings:mb-2 prose-headings:mt-4 prose-headings:font-semibold prose-p:my-2 prose-pre:my-2 prose-pre:bg-gray-800 prose-pre:text-gray-100 prose-code:rounded prose-code:bg-gray-200 prose-code:px-1 prose-code:py-0.5 prose-code:text-gray-800 prose-code:before:content-none prose-code:after:content-none prose-pre:prose-code:bg-transparent prose-pre:prose-code:p-0 prose-pre:prose-code:text-gray-100 prose-ul:my-2 prose-ol:my-2 prose-li:my-0">
                    <Markdown remarkPlugins={[remarkGfm]}>
                      {msg.content}
                    </Markdown>
                  </div>
                )}
              </div>
            </div>
          ))}
          {sending && (
            <div className="mb-4 flex justify-start">
              <div className="flex items-center gap-2 rounded-lg bg-gray-100 px-4 py-2 text-gray-500">
                <Spinner size="xs" />
                <span className="text-sm">{t("Thinking...")}</span>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Input */}
        <form
          onSubmit={handleSubmit}
          className="border-t p-4"
        >
          <div className="flex gap-2">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder={t("Type your message...")}
              disabled={sending}
              className="flex-1 rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500 disabled:bg-gray-50"
            />
            <button
              type="submit"
              disabled={sending || !input.trim()}
              className="rounded-md bg-blue-600 px-4 py-2 text-white hover:bg-blue-700 disabled:opacity-50"
            >
              <PaperAirplaneIcon className="h-5 w-5" />
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default AssistantChat;

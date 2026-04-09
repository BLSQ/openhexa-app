import { PaperAirplaneIcon } from "@heroicons/react/24/outline";
import clsx from "clsx";
import Spinner from "core/components/Spinner";
import { KeyboardEvent, ReactNode, useCallback, useEffect, useRef, useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import {
  AssistantConversationMessagesDocument,
  AssistantConversationMessagesQuery,
  useAssistantConversationMessagesQuery,
} from "assistant/graphql/queries.generated";
import { useSendAssistantMessageMutation } from "assistant/graphql/mutations.generated";

const PER_PAGE = 20;

type Message = NonNullable<
  AssistantConversationMessagesQuery["assistantConversation"]
>["messages"]["items"][0];

type Props = {
  conversationId: string | null;
  monthlyLimitExceeded: boolean;
  // If provided and conversationId is null, called on the first send to lazily create a conversation.
  // Should return the new conversation id, or null on failure.
  createConversation?: () => Promise<string | null>;
  // Called after a new conversation is successfully created via createConversation.
  onConversationCreated?: (id: string) => void;
  // Called whenever the message list changes (e.g. after a new assistant reply).
  onMessagesChange?: (messages: Message[]) => void;
  // Optional per-message renderer. Rendered below each assistant message bubble.
  renderMessageAfter?: (message: Message) => ReactNode;
};

export default function ChatPane({
  conversationId,
  monthlyLimitExceeded,
  createConversation,
  onConversationCreated,
  onMessagesChange,
  renderMessageAfter,
}: Props) {
  const [input, setInput] = useState("");
  const [localConversationId, setLocalConversationId] = useState<string | null>(
    conversationId,
  );
  const bottomRef = useRef<HTMLDivElement>(null);
  const scrollContainerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    setLocalConversationId(conversationId);
  }, [conversationId]);

  const { data, loading: loadingMessages, fetchMore } =
    useAssistantConversationMessagesQuery({
      variables: { id: localConversationId!, page: 1, perPage: PER_PAGE },
      skip: !localConversationId,
    });

  const messagePage = data?.assistantConversation?.messages;
  const totalPages = messagePage?.totalPages ?? 1;
  const [currentPage, setCurrentPage] = useState(1);
  const [loadingMore, setLoadingMore] = useState(false);
  const hasMore = currentPage < totalPages;

  useEffect(() => {
    setCurrentPage(1);
  }, [localConversationId]);

  // Messages come back newest-first from the API; reverse for chronological display
  const messages = [...(messagePage?.items ?? [])].reverse();

  useEffect(() => {
    if (messages.length > 0) onMessagesChange?.(messages);
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [messagePage]);

  const [pendingUserMessage, setPendingUserMessage] = useState<string | null>(null);

  const [sendMessage, { loading: sending }] = useSendAssistantMessageMutation({
    onCompleted: () => {
      setCurrentPage(1);
      setPendingUserMessage(null);
    },
  });

  useEffect(() => {
    if (!loadingMessages) {
      bottomRef.current?.scrollIntoView({ behavior: "smooth" });
    }
  }, [loadingMessages, localConversationId]);

  useEffect(() => {
    if (!loadingMore) {
      bottomRef.current?.scrollIntoView({ behavior: "smooth" });
    }
  }, [messages.length, pendingUserMessage]);

  const loadOlderMessages = useCallback(async () => {
    if (loadingMore || !hasMore || !localConversationId) return;

    const container = scrollContainerRef.current;
    const previousScrollHeight = container?.scrollHeight ?? 0;

    setLoadingMore(true);
    const nextPage = currentPage + 1;

    await fetchMore({
      variables: { id: localConversationId, page: nextPage, perPage: PER_PAGE },
      updateQuery(prev, { fetchMoreResult }) {
        if (!fetchMoreResult?.assistantConversation) return prev;
        const prevItems = prev.assistantConversation?.messages.items ?? [];
        const newItems = fetchMoreResult.assistantConversation.messages.items;
        const merged = [
          ...prevItems,
          ...newItems.filter((n) => !prevItems.some((p) => p.id === n.id)),
        ];
        return {
          ...prev,
          assistantConversation: {
            ...fetchMoreResult.assistantConversation,
            messages: {
              ...fetchMoreResult.assistantConversation.messages,
              items: merged,
            },
          },
        };
      },
    });

    setCurrentPage(nextPage);
    setLoadingMore(false);

    requestAnimationFrame(() => {
      if (container) {
        container.scrollTop = container.scrollHeight - previousScrollHeight;
      }
    });
  }, [loadingMore, hasMore, localConversationId, currentPage, fetchMore]);

  const handleScroll = useCallback(() => {
    const container = scrollContainerRef.current;
    if (!container) return;
    if (container.scrollTop === 0 && hasMore && !loadingMore) {
      loadOlderMessages();
    }
  }, [hasMore, loadingMore, loadOlderMessages]);

  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    const el = textareaRef.current;
    if (!el) return;
    el.style.height = "auto";
    el.style.height = `${el.scrollHeight}px`;
  }, [input]);

  const handleSubmit = async () => {
    const text = input.trim();
    if (!text || sending || monthlyLimitExceeded) return;

    let convId = localConversationId;

    if (!convId && createConversation) {
      convId = await createConversation();
      if (!convId) return;
      setLocalConversationId(convId);
      onConversationCreated?.(convId);
    }

    if (!convId) return;

    setPendingUserMessage(text);
    setInput("");
    await sendMessage({
      variables: { input: { conversationId: convId, message: text } },
      refetchQueries: [
        {
          query: AssistantConversationMessagesDocument,
          variables: { id: convId, page: 1, perPage: PER_PAGE },
        },
      ],
    });
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const isLazy = !localConversationId && !!createConversation;

  if (!localConversationId && !isLazy) {
    return (
      <div className="flex flex-1 items-center justify-center text-sm text-gray-400">
        Select a conversation or create a new one
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full overflow-hidden bg-white">
      <div className="flex-1 flex flex-col p-4 max-w-3xl mx-auto w-full min-h-0">
        <div
          ref={scrollContainerRef}
          onScroll={handleScroll}
          className="flex-1 overflow-y-auto min-h-0 space-y-4"
        >
          {loadingMore && (
            <div className="flex justify-center py-2">
              <Spinner size="sm" className="text-gray-400" />
            </div>
          )}

          {loadingMessages && (
            <div className="flex justify-center pt-8">
              <Spinner size="md" className="text-gray-400" />
            </div>
          )}

          {messages.map((msg) => (
            <div key={msg.id}>
              <div
                className={clsx(
                  "flex",
                  msg.role === "user" ? "justify-end" : "justify-start",
                )}
              >
                <div
                  className={clsx(
                    "max-w-2xl rounded-2xl px-4 py-3 text-sm",
                    msg.role === "user"
                      ? "bg-blue-600 text-white whitespace-pre-wrap"
                      : "bg-gray-100 text-gray-900",
                  )}
                >
                  {msg.role === "user" ? (
                    msg.content
                  ) : (
                    <div className="prose prose-sm prose-gray max-w-none">
                      <ReactMarkdown remarkPlugins={[remarkGfm]}>
                        {msg.content}
                      </ReactMarkdown>
                    </div>
                  )}
                </div>
              </div>
              {renderMessageAfter?.(msg)}
            </div>
          ))}

          {pendingUserMessage && (
            <div className="flex justify-end">
              <div className="max-w-2xl rounded-2xl px-4 py-3 text-sm bg-blue-600 text-white whitespace-pre-wrap">
                {pendingUserMessage}
              </div>
            </div>
          )}

          {sending && (
            <div className="flex justify-start">
              <div className="rounded-2xl bg-gray-100 px-4 py-3">
                <Spinner size="xs" className="text-gray-400" />
              </div>
            </div>
          )}

          <div ref={bottomRef} />
        </div>

        {monthlyLimitExceeded ? (
          <div className="shrink-0 mt-4 rounded-2xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
            You have reached your monthly usage limit for the assistant. Please
            contact your administrator.
          </div>
        ) : (
          <div
            className="shrink-0 mt-4 rounded-2xl border border-gray-300 bg-white shadow-sm focus-within:border-blue-500 focus-within:ring-1 focus-within:ring-blue-500 cursor-text"
            onClick={() => textareaRef.current?.focus()}
          >
            <textarea
              ref={textareaRef}
              className="w-full resize-none bg-transparent px-4 pt-3 pb-2 text-sm focus:outline-none disabled:opacity-50"
              style={{ maxHeight: "200px", overflowY: "auto" }}
              rows={1}
              placeholder="Message… (Enter to send, Shift+Enter for newline)"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              disabled={sending}
            />
            <div className="flex items-center justify-end px-2 pb-2">
              <button
                onClick={handleSubmit}
                disabled={!input.trim() || sending}
                className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-blue-600 text-white transition-colors hover:bg-blue-700 disabled:opacity-40 disabled:cursor-not-allowed"
              >
                <PaperAirplaneIcon className="h-4 w-4" />
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

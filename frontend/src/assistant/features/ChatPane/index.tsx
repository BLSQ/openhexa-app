import { PaperAirplaneIcon } from "@heroicons/react/24/outline";
import clsx from "clsx";
import Spinner from "core/components/Spinner";
import { KeyboardEvent, useEffect, useRef, useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import {
  AssistantConversationMessagesDocument,
  useAssistantConversationMessagesQuery,
} from "assistant/graphql/queries.generated";
import { useSendAssistantMessageMutation } from "assistant/graphql/mutations.generated";

type Props = {
  conversationId: string | null;
};

export default function ChatPane({ conversationId }: Props) {
  const [input, setInput] = useState("");
  const bottomRef = useRef<HTMLDivElement>(null);

  const { data, loading: loadingMessages } =
    useAssistantConversationMessagesQuery({
      variables: { id: conversationId! },
      skip: !conversationId,
    });

  const [sendMessage, { loading: sending }] = useSendAssistantMessageMutation({
    refetchQueries: conversationId
      ? [
          {
            query: AssistantConversationMessagesDocument,
            variables: { id: conversationId },
          },
        ]
      : [],
    onCompleted: () => setInput(""),
  });

  const messages = data?.assistantConversation?.messages ?? [];

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSubmit = async () => {
    const text = input.trim();
    if (!text || !conversationId || sending) return;

    await sendMessage({
      variables: { input: { conversationId, message: text } },
    });
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  if (!conversationId) {
    return (
      <div className="flex flex-1 items-center justify-center text-sm text-gray-400">
        Select a conversation or create a new one
      </div>
    );
  }

  return (
    <div className="flex flex-1 flex-col overflow-hidden bg-white">
      <div className="flex-1 overflow-y-auto p-6 space-y-4">
        {loadingMessages && (
          <div className="flex justify-center pt-8">
            <Spinner size="md" className="text-gray-400" />
          </div>
        )}

        {messages.map((msg) => (
          <div
            key={msg.id}
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
        ))}

        {sending && (
          <div className="flex justify-start">
            <div className="rounded-2xl bg-gray-100 px-4 py-3">
              <Spinner size="xs" className="text-gray-400" />
            </div>
          </div>
        )}

        <div ref={bottomRef} />
      </div>

      <div className="shrink-0 border-t border-gray-200 p-4">
        <div className="flex items-end gap-3">
          <textarea
            className="flex-1 resize-none rounded-lg border border-gray-300 px-4 py-3 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500 disabled:opacity-50"
            rows={3}
            placeholder="Type a message… (Enter to send, Shift+Enter for newline)"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            disabled={sending}
          />
          <button
            onClick={handleSubmit}
            disabled={!input.trim() || sending}
            className="flex h-11 w-11 shrink-0 items-center justify-center rounded-lg bg-blue-600 text-white transition-colors hover:bg-blue-700 disabled:opacity-40 disabled:cursor-not-allowed"
          >
            <PaperAirplaneIcon className="h-5 w-5" />
          </button>
        </div>
      </div>
    </div>
  );
}

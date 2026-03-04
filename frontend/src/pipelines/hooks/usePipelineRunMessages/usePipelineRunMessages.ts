import { useEffect, useState } from "react";

export type SseMessage = {
  message: string;
  timestamp: string | null;
  priority: string;
};

type UsePipelineRunMessagesReturn = {
  messages: SseMessage[];
  isStreaming: boolean;
};

function usePipelineRunMessages(runId: string): UsePipelineRunMessagesReturn {
  const [messages, setMessages] = useState<SseMessage[]>([]);
  const [isStreaming, setIsStreaming] = useState(false);

  useEffect(() => {
    const apiBasePath = process.env.NEXT_PUBLIC_API_BASE_PATH ?? "";
    const url = `${apiBasePath}/pipelines/runs/${runId}/messages/stream/`;
    const source = new EventSource(url, { withCredentials: true });

    setIsStreaming(true);

    source.addEventListener("message", (e: MessageEvent) => {
      const data = JSON.parse(e.data) as SseMessage;
      setMessages((prev) => [...prev, data]);
    });

    source.addEventListener("done", () => {
      source.close();
      setIsStreaming(false);
    });

    source.addEventListener("error", () => {
      source.close();
      setIsStreaming(false);
    });

    return () => {
      source.close();
      setIsStreaming(false);
    };
  }, [runId]);

  return { messages, isStreaming };
}

export default usePipelineRunMessages;

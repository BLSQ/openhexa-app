import * as Sentry from "@sentry/nextjs";
import { getPublicEnv } from "core/helpers/runtimeConfig";
import { useEffect, useState } from "react";

export type SseMessage = {
  message: string;
  timestamp: string | null;
  priority: string;
};

type UsePipelineRunMessagesReturn = {
  messages: SseMessage[];
  isStreaming: boolean;
  streamError: string | null;
};

function usePipelineRunMessages(
  runId: string,
  isTerminal: boolean,
  onDone?: () => void,
): UsePipelineRunMessagesReturn {
  const [messages, setMessages] = useState<SseMessage[]>([]);
  const [isStreaming, setIsStreaming] = useState(false);
  const [streamError, setStreamError] = useState<string | null>(null);

  useEffect(() => {
    if (isTerminal) return;

    const apiBasePath =
      process.env.NEXT_PUBLIC_API_BASE_PATH ??
      getPublicEnv().OPENHEXA_BACKEND_URL;
    const url = `${apiBasePath}/pipelines/runs/${runId}/messages/stream/`;
    const source = new EventSource(url, { withCredentials: true });

    setMessages([]);
    setIsStreaming(true);
    setStreamError(null);

    source.addEventListener("message", (e: MessageEvent) => {
      const data = JSON.parse(e.data) as SseMessage;
      setMessages((prev) => [...prev, data]);
    });

    source.addEventListener("done", () => {
      source.close();
      setIsStreaming(false);
      onDone?.();
    });

    source.addEventListener("timeout", () => {
      source.close();
      setIsStreaming(false);
      setStreamError("timeout");
      Sentry.captureMessage("SSE pipeline run messages timed out", {
        level: "warning",
        extra: { runId },
      });
    });

    source.addEventListener("error", () => {
      source.close();
      setIsStreaming(false);
      setStreamError("connection_failed");
      Sentry.captureException(
        new Error(`SSE connection failed for pipeline run ${runId}`),
      );
    });

    return () => {
      source.close();
      setIsStreaming(false);
    };
  }, [runId, isTerminal]);

  return { messages, isStreaming, streamError };
}

export default usePipelineRunMessages;

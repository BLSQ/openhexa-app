import * as Sentry from "@sentry/nextjs";
import { getPublicEnv } from "core/helpers/runtimeConfig";
import useSSE from "core/hooks/useSSE";
import { useEffect, useMemo, useRef, useState } from "react";

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
  const [streamError, setStreamError] = useState<string | null>(null);
  const cleanCloseRef = useRef(false);

  useEffect(() => {
    setMessages([]);
    setStreamError(null);
    cleanCloseRef.current = false;
  }, [runId]);

  const url = useMemo(() => {
    if (isTerminal) return null;
    const apiBasePath =
      process.env.NEXT_PUBLIC_API_BASE_PATH ??
      getPublicEnv().OPENHEXA_BACKEND_URL;
    return `${apiBasePath}/pipelines/runs/${runId}/messages/stream/`;
  }, [runId, isTerminal]);

  const { isConnected: isStreaming, connectionError } = useSSE(url, {
    message: (data) => {
      setMessages((prev) => [...prev, data as SseMessage]);
    },
    done: () => {
      cleanCloseRef.current = true;
      onDone?.();
    },
    timeout: () => {
      setStreamError("timeout");
      Sentry.captureMessage("SSE pipeline run messages timed out", {
        level: "warning",
        extra: { runId },
      });
    },
  });

  useEffect(() => {
    if (connectionError && !cleanCloseRef.current) {
      setStreamError("connection_failed");
      Sentry.captureException(
        new Error(`SSE connection failed for pipeline run ${runId}`),
      );
    }
  }, [connectionError, runId]);

  return { messages, isStreaming, streamError };
}

export default usePipelineRunMessages;

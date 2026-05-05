import { getPublicEnv } from "core/helpers/runtimeConfig";
import useSSE from "core/hooks/useSSE";
import { useCallback, useEffect, useMemo, useRef, useState } from "react";

export type SseMessage = {
  message: string;
  timestamp: string | null;
  priority: string;
};

type UsePipelineRunMessagesReturn = {
  messages: SseMessage[];
  isStreaming: boolean;
  streamError: string | null;
  reload: () => void;
};

type ReloadState = { cursor: number; attempt: number };

function usePipelineRunMessages(
  runId: string,
  isTerminal: boolean,
  onDone?: () => void,
): UsePipelineRunMessagesReturn {
  const [messages, setMessages] = useState<SseMessage[]>([]);
  const [streamError, setStreamError] = useState<string | null>(null);
  const [reloadState, setReloadState] = useState<ReloadState | null>(null);
  const cleanCloseRef = useRef(false);
  const messagesRef = useRef<SseMessage[]>([]);
  messagesRef.current = messages;

  useEffect(() => {
    setMessages([]);
    setStreamError(null);
    setReloadState(null);
    cleanCloseRef.current = false;
  }, [runId]);

  const url = useMemo(() => {
    if (isTerminal) return null;
    const apiBasePath =
      process.env.NEXT_PUBLIC_API_BASE_PATH ||
      getPublicEnv().OPENHEXA_BACKEND_URL;
    const base = `${apiBasePath}/pipelines/runs/${runId}/messages/stream/`;
    if (!reloadState) return base;
    return `${base}?from=${reloadState.cursor}&_attempt=${reloadState.attempt}`;
  }, [runId, isTerminal, reloadState]);

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
    },
  });

  useEffect(() => {
    if (connectionError && !cleanCloseRef.current) {
      setStreamError("connection_failed");
    }
  }, [connectionError]);

  const reload = useCallback(() => {
    cleanCloseRef.current = false;
    setStreamError(null);
    setReloadState((prev) => ({
      cursor: messagesRef.current.length,
      attempt: (prev?.attempt ?? 0) + 1,
    }));
  }, []);

  return { messages, isStreaming, streamError, reload };
}

export default usePipelineRunMessages;

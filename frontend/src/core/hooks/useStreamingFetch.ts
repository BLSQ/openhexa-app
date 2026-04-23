import { useCallback, useEffect, useRef, useState } from "react";

type StreamHandlers = {
  [eventType: string]: (data: unknown) => void;
};

type UseStreamingFetchReturn = {
  send: (url: string, body: Record<string, unknown>) => Promise<void>;
  isStreaming: boolean;
  streamError: string | null;
};

function parseSSEBlocks(
  buffer: string,
  handlers: StreamHandlers,
): string {
  const blocks = buffer.split("\n\n");
  const remaining = blocks.pop() ?? "";

  for (const block of blocks) {
    let eventType = "message";
    let dataLine = "";

    for (const line of block.split("\n")) {
      if (line.startsWith("event: ")) {
        eventType = line.slice(7).trim();
      } else if (line.startsWith("data: ")) {
        dataLine = line.slice(6);
      }
    }

    if (dataLine) {
      try {
        handlers[eventType]?.(JSON.parse(dataLine));
      } catch {
        // ignore malformed data lines
      }
    }
  }

  return remaining;
}

function useStreamingFetch(handlers: StreamHandlers): UseStreamingFetchReturn {
  const [isStreaming, setIsStreaming] = useState(false);
  const [streamError, setStreamError] = useState<string | null>(null);
  const handlersRef = useRef(handlers);
  handlersRef.current = handlers;
  const abortRef = useRef<AbortController | null>(null);

  const send = useCallback(
    async (url: string, body: Record<string, unknown>) => {
      abortRef.current?.abort();

      const controller = new AbortController();
      abortRef.current = controller;

      setIsStreaming(true);
      setStreamError(null);

      try {
        const response = await fetch(url, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          credentials: "include",
          body: JSON.stringify(body),
          signal: controller.signal,
        });

        if (!response.ok) {
          throw new Error(`HTTP ${response.status}`);
        }

        if (!response.body) {
          throw new Error("No response body");
        }

        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let buffer = "";

        while (true) {
          const { done, value } = await reader.read();
          if (done) break;
          buffer += decoder.decode(value, { stream: true });
          buffer = parseSSEBlocks(buffer, handlersRef.current);
        }

        if (buffer.trim()) {
          parseSSEBlocks(buffer + "\n\n", handlersRef.current);
        }
      } catch (error) {
        if ((error as Error).name !== "AbortError") {
          setStreamError("connection_failed");
        }
      } finally {
        setIsStreaming(false);
        abortRef.current = null;
      }
    },
    [],
  );

  useEffect(() => {
    return () => abortRef.current?.abort();
  }, []);

  return { send, isStreaming, streamError };
}

export default useStreamingFetch;

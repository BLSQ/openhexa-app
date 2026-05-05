import { useEffect, useRef, useState } from "react";

type UseSSEHandlers = {
  [eventType: string]: (data: unknown) => void;
};

type UseSSEReturn = {
  isConnected: boolean;
  connectionError: boolean;
  close: () => void;
};

function useSSE(url: string | null, handlers: UseSSEHandlers): UseSSEReturn {
  const [isConnected, setIsConnected] = useState(false);
  const [connectionError, setConnectionError] = useState(false);
  const handlersRef = useRef(handlers);
  handlersRef.current = handlers;
  const sourceRef = useRef<EventSource | null>(null);

  useEffect(() => {
    if (!url) {
      setIsConnected(false);
      setConnectionError(false);
      return;
    }

    const source = new EventSource(url, { withCredentials: true });
    sourceRef.current = source;
    setConnectionError(false);

    source.onopen = () => {
      setIsConnected(true);
    };

    const eventTypes = Object.keys(handlersRef.current);
    eventTypes.forEach((eventType) => {
      source.addEventListener(eventType, (e: MessageEvent) => {
        handlersRef.current[eventType]?.(JSON.parse(e.data));
      });
    });

    source.onerror = () => {
      source.close();
      sourceRef.current = null;
      setIsConnected(false);
      setConnectionError(true);
    };

    return () => {
      source.close();
      sourceRef.current = null;
      setIsConnected(false);
    };
  }, [url]);

  const close = () => {
    sourceRef.current?.close();
    sourceRef.current = null;
    setIsConnected(false);
  };

  return { isConnected, connectionError, close };
}

export default useSSE;

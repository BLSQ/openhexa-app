import { useEffect, useRef, useState } from "react";

type UseSSEHandlers = {
  [eventType: string]: (data: unknown) => void;
};

type UseSSEReturn = {
  isConnected: boolean;
  connectionError: boolean;
};

function useSSE(url: string | null, handlers: UseSSEHandlers): UseSSEReturn {
  const [isConnected, setIsConnected] = useState(false);
  const [connectionError, setConnectionError] = useState(false);
  const handlersRef = useRef(handlers);
  handlersRef.current = handlers;

  useEffect(() => {
    if (!url) {
      setIsConnected(false);
      setConnectionError(false);
      return;
    }

    const source = new EventSource(url, { withCredentials: true });
    setIsConnected(true);
    setConnectionError(false);

    const eventTypes = Object.keys(handlersRef.current);
    eventTypes.forEach((eventType) => {
      source.addEventListener(eventType, (e: MessageEvent) => {
        handlersRef.current[eventType]?.(JSON.parse(e.data));
      });
    });

    source.onerror = () => {
      source.close();
      setIsConnected(false);
      setConnectionError(true);
    };

    return () => {
      source.close();
      setIsConnected(false);
    };
  }, [url]);

  return { isConnected, connectionError };
}

export default useSSE;

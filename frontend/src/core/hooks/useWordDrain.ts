import { useCallback, useEffect, useRef, useState } from "react";

type Options = {
  interval?: number;
  onDrained?: () => void;
};

type UseWordDrainReturn = {
  text: string | null;
  feed: (chunk: string) => void;
  markDone: () => void;
  clear: () => void;
};

function useWordDrain({ interval = 30, onDrained }: Options = {}): UseWordDrainReturn {
  const [text, setText] = useState<string | null>(null);
  const queueRef = useRef("");
  const doneRef = useRef(false);
  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const onDrainedRef = useRef(onDrained);
  onDrainedRef.current = onDrained;

  const stop = useCallback(() => {
    if (timerRef.current !== null) {
      clearInterval(timerRef.current);
      timerRef.current = null;
    }
  }, []);

  const start = useCallback(() => {
    if (timerRef.current !== null) return;
    timerRef.current = setInterval(() => {
      if (queueRef.current.length > 0) {
        const spaceIdx = queueRef.current.search(/\s/);
        if (spaceIdx !== -1) {
          const token = queueRef.current.slice(0, spaceIdx + 1);
          queueRef.current = queueRef.current.slice(spaceIdx + 1);
          setText((prev) => (prev ?? "") + token);
        } else if (doneRef.current) {
          const remaining = queueRef.current;
          queueRef.current = "";
          setText((prev) => (prev ?? "") + remaining);
        }
        // else: mid-word, more text coming — wait for whitespace boundary
      } else if (doneRef.current) {
        stop();
        doneRef.current = false;
        setText(null);
        onDrainedRef.current?.();
      }
    }, interval);
  }, [stop, interval]);

  useEffect(() => stop, [stop]);

  const feed = useCallback(
    (chunk: string) => {
      queueRef.current += chunk;
      start();
    },
    [start],
  );

  const markDone = useCallback(() => {
    doneRef.current = true;
    start();
  }, [start]);

  const clear = useCallback(() => {
    queueRef.current = "";
    doneRef.current = false;
    stop();
    setText(null);
  }, [stop]);

  return { text, feed, markDone, clear };
}

export default useWordDrain;

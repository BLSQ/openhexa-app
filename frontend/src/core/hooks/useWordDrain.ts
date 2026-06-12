import { useCallback, useEffect, useRef, useState } from "react";

type Options = {
  /** Milliseconds between each word reveal tick. */
  interval?: number;
  /** Called once the queue is fully drained after `markDone()` has been called. */
  onDrained?: () => void;
};

type UseWordDrainReturn = {
  /** The progressively revealed text, or `null` when idle / after draining. */
  text: string | null;
  /** Append an incoming SSE chunk to the internal queue and start draining. */
  feed: (chunk: string) => void;
  /**
   * Signal that no more chunks will arrive.
   * The hook finishes draining the queue (including any trailing partial word),
   * then calls `onDrained` and resets `text` to `null`.
   */
  markDone: () => void;
  /** Immediately discard the queue and reset to idle without calling `onDrained`. */
  clear: () => void;
  /**
   * Snapshot all text fed so far, then immediately reset to idle (like `clear`).
   * Use this when a mid-stream event (e.g. a tool call) needs to capture the
   * accumulated text as a completed segment before resuming.
   */
  flush: () => string;
};

/**
 * Streams text to the UI word-by-word as SSE chunks arrive.
 *
 * Call `feed(chunk)` for each arriving chunk and `markDone()` when the stream
 * ends. The hook reveals text one word at a time (splitting at whitespace) so
 * partial words never flash on screen mid-stream.
 *
 * The timer only runs while there is text in the queue, which avoids busy-
 * looping between messages. After `markDone()` empties the queue, `onDrained`
 * fires and `text` resets to `null`, making the hook ready for the next message.
 */
function useWordDrain({ interval = 30, onDrained }: Options = {}): UseWordDrainReturn {
  const [text, setText] = useState<string | null>(null);
  const queueRef = useRef("");
  const allTextRef = useRef("");
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
        allTextRef.current = "";
        setText(null);
        onDrainedRef.current?.();
      }
    }, interval);
  }, [stop, interval]);

  useEffect(() => stop, [stop]);

  const feed = useCallback(
    (chunk: string) => {
      queueRef.current += chunk;
      allTextRef.current += chunk;
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
    allTextRef.current = "";
    doneRef.current = false;
    stop();
    setText(null);
  }, [stop]);

  const flush = useCallback((): string => {
    const captured = allTextRef.current;
    clear();
    return captured;
  }, [clear]);

  return { text, feed, markDone, clear, flush };
}

export default useWordDrain;

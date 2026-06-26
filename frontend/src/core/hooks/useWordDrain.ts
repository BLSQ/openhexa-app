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
  /**
   * `true` while there is still queued text waiting to be revealed. Goes back to
   * `false` once the visible text has caught up with everything fed so far, which
   * lets callers show a "thinking" state during the gaps between chunks (e.g.
   * while a tool call is being prepared).
   */
  pending: boolean;
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
 * Partial words are normally held back until a whitespace boundary arrives so a
 * half-typed word never flashes on screen. If the stream stalls mid-word (which
 * happens right before a tool call, while no `done` has been sent yet), the
 * trailing word is revealed anyway after a short idle grace period so it is not
 * left stranded and cut off on screen.
 *
 * After `markDone()` empties the queue, `onDrained` fires and `text` resets to
 * `null`, making the hook ready for the next message.
 */
const IDLE_REVEAL_TICKS = 3;

function useWordDrain({ interval = 30, onDrained }: Options = {}): UseWordDrainReturn {
  const [text, setText] = useState<string | null>(null);
  const [pending, setPending] = useState(false);
  const queueRef = useRef("");
  const allTextRef = useRef("");
  const doneRef = useRef(false);
  const idleTicksRef = useRef(0);
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
          idleTicksRef.current = 0;
          const token = queueRef.current.slice(0, spaceIdx + 1);
          queueRef.current = queueRef.current.slice(spaceIdx + 1);
          setText((prev) => (prev ?? "") + token);
          if (queueRef.current.length === 0) setPending(false);
        } else if (doneRef.current || idleTicksRef.current >= IDLE_REVEAL_TICKS) {
          // No whitespace boundary, but the stream has ended or stalled — reveal
          // the trailing word rather than leaving it stranded off-screen.
          idleTicksRef.current = 0;
          const remaining = queueRef.current;
          queueRef.current = "";
          setText((prev) => (prev ?? "") + remaining);
          setPending(false);
        } else {
          idleTicksRef.current += 1;
        }
      } else if (doneRef.current) {
        stop();
        doneRef.current = false;
        idleTicksRef.current = 0;
        allTextRef.current = "";
        setText(null);
        setPending(false);
        onDrainedRef.current?.();
      } else {
        // Caught up with everything fed so far and not done — idle until the
        // next chunk or markDone(), instead of busy-looping.
        stop();
      }
    }, interval);
  }, [stop, interval]);

  useEffect(() => stop, [stop]);

  const feed = useCallback(
    (chunk: string) => {
      queueRef.current += chunk;
      allTextRef.current += chunk;
      idleTicksRef.current = 0;
      setPending(true);
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
    idleTicksRef.current = 0;
    stop();
    setText(null);
    setPending(false);
  }, [stop]);

  const flush = useCallback((): string => {
    const captured = allTextRef.current;
    clear();
    return captured;
  }, [clear]);

  return { text, pending, feed, markDone, clear, flush };
}

export default useWordDrain;

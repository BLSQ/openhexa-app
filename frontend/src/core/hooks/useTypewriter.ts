import { useEffect, useRef, useState } from "react";

type Options = {
  /** Milliseconds between each character reveal. */
  interval?: number;
};

/**
 * Reveals a static string character-by-character at a fixed interval.
 *
 * Designed for one-shot strings (e.g. a conversation name received via SSE):
 * when `value` changes the animation resets from scratch, so it is not suited
 * for incrementally-arriving chunks — use `useWordDrain` for that.
 *
 * Returns `null` while `value` is falsy, `""` on the first tick, then the
 * progressively growing string until the full value is displayed.
 */
function useTypewriter(value: string | null, { interval = 35 }: Options = {}): string | null {
  const [displayed, setDisplayed] = useState<string | null>(null);
  const queueRef = useRef("");

  useEffect(() => {
    if (!value) {
      setDisplayed(null);
      return;
    }
    queueRef.current = value;
    setDisplayed("");
    const timer = setInterval(() => {
      if (queueRef.current.length > 0) {
        const char = queueRef.current[0];
        queueRef.current = queueRef.current.slice(1);
        setDisplayed((prev) => (prev ?? "") + char);
      } else {
        clearInterval(timer);
      }
    }, interval);
    return () => clearInterval(timer);
  }, [value, interval]);

  return displayed;
}

export default useTypewriter;

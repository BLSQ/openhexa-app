import { useEffect, useRef, useState } from "react";

type Options = {
  interval?: number;
};

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

import { useEffect, useState } from "react";

interface Args extends IntersectionObserverInit {
  freezeOnceVisible?: boolean;
}

export default function useIntersectionObserver(
  element: Element | null,
  {
    threshold = 0,
    root = null,
    rootMargin = "0%",
    freezeOnceVisible = false,
  }: Args,
): IntersectionObserverEntry | undefined {
  const [entry, setEntry] = useState<IntersectionObserverEntry>();

  const frozen = entry?.isIntersecting && freezeOnceVisible;

  const updateEntry = ([entry]: IntersectionObserverEntry[]): void => {
    setEntry(entry);
  };

  useEffect(() => {
    const hasIOSupport = !!window.IntersectionObserver;

    if (!hasIOSupport || frozen || !element) {
      return;
    }

    const observerParams = { threshold, root, rootMargin };
    const observer = new IntersectionObserver(updateEntry, observerParams);

    observer.observe(element);

    return () => observer.disconnect();

    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [element, threshold, root, rootMargin, frozen]);

  return entry;
}

import { useEffect, useRef } from "react";

const useAutoScroll = (
  scrollableContentRef: React.RefObject<HTMLElement>,
  scrollBehavior: "auto" | "smooth" = "auto",
) => {
  const isAutoScrollActive = useRef<boolean>(true);
  const lastScrollTop = useRef<number>(0);

  useEffect(() => {
    const child = scrollableContentRef.current;
    const parent = child?.parentElement;
    if (child && parent) {
      const resizeObserver = new ResizeObserver(() => {
        if (isAutoScrollActive.current) {
          parent.scrollTo({
            top: child.scrollHeight,
            behavior: scrollBehavior,
          });
        }
      });

      resizeObserver.observe(child);

      const onScroll = (event: any) => {
        const { scrollTop, scrollHeight } = event.target;
        const isScrolledToBottom = scrollHeight === child.scrollHeight;
        if (scrollTop < lastScrollTop.current && lastScrollTop.current !== 0) {
          isAutoScrollActive.current = false;
        } else if (isScrolledToBottom) {
          isAutoScrollActive.current = true;
        }

        lastScrollTop.current = scrollTop;
      };
      // Observe scroll position
      parent.addEventListener("scroll", onScroll);

      // Scroll to bottom on mount
      parent.scrollTo({
        top: parent.scrollHeight,
        behavior: "auto",
      });

      return () => {
        resizeObserver.unobserve(child);
        parent.removeEventListener("scroll", onScroll);
      };
    }
  }, [scrollableContentRef, scrollBehavior]);

  useEffect(() => {
    isAutoScrollActive.current = true;
    lastScrollTop.current = 0;
  }, [scrollableContentRef]);
};

export default useAutoScroll;

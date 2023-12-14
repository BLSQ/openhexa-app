import { useEffect, useRef } from "react";

const useAutoScroll = (
  scrollableContentRef: React.RefObject<HTMLElement>,
  scrollBehavior: "auto" | "smooth" = "auto",
) => {
  const isScrolledToBottomRef = useRef<boolean>(true);

  useEffect(() => {
    const child = scrollableContentRef.current;
    const parent = child?.parentElement;
    if (child && parent) {
      const resizeObserver = new ResizeObserver(() => {
        if (isScrolledToBottomRef.current) {
          parent.scrollTo({
            top: parent.scrollHeight + 10,
            behavior: scrollBehavior,
          });
        }
      });

      resizeObserver.observe(child);

      const onScroll = (event: any) => {
        const { scrollTop, scrollHeight, clientHeight } = event.target;
        const isScrolledToBottom = scrollHeight - scrollTop === clientHeight;
        isScrolledToBottomRef.current = isScrolledToBottom;
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
};

export default useAutoScroll;

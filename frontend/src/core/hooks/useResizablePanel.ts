import { RefObject, useCallback, useEffect, useState } from "react";

type UseResizablePanelOptions = {
  storageKey: string;
  containerRef: RefObject<HTMLElement | null>;
  defaultWidth?: number;
  minWidth?: number;
  maxWidth?: number;
};

const useResizablePanel = ({
  storageKey,
  containerRef,
  defaultWidth = 440,
  minWidth = 280,
  maxWidth = 720,
}: UseResizablePanelOptions) => {
  const clamp = useCallback(
    (width: number) => Math.min(maxWidth, Math.max(minWidth, width)),
    [minWidth, maxWidth],
  );

  const [width, setWidth] = useState(defaultWidth);
  const [isDragging, setIsDragging] = useState(false);

  useEffect(() => {
    const stored = window.localStorage.getItem(storageKey);
    if (stored === null) return;
    const parsed = Number(stored);
    if (!Number.isNaN(parsed)) {
      setWidth(clamp(parsed));
    }
  }, [storageKey, clamp]);

  useEffect(() => {
    if (!isDragging) return;

    const handleMove = (event: MouseEvent) => {
      const rect = containerRef.current?.getBoundingClientRect();
      if (!rect) return;
      setWidth(clamp(rect.right - event.clientX));
    };
    const handleUp = () => setIsDragging(false);

    document.addEventListener("mousemove", handleMove);
    document.addEventListener("mouseup", handleUp);
    // Keep the cursor consistent even when the pointer outruns the handle.
    const previousUserSelect = document.body.style.userSelect;
    document.body.style.userSelect = "none";
    document.body.style.cursor = "col-resize";

    return () => {
      document.removeEventListener("mousemove", handleMove);
      document.removeEventListener("mouseup", handleUp);
      document.body.style.userSelect = previousUserSelect;
      document.body.style.cursor = "";
    };
  }, [isDragging, containerRef, clamp]);

  useEffect(() => {
    if (isDragging) return;
    window.localStorage.setItem(storageKey, String(width));
  }, [isDragging, width, storageKey]);

  const startDragging = useCallback(() => setIsDragging(true), []);
  const resetWidth = useCallback(() => setWidth(defaultWidth), [defaultWidth]);

  return { width, isDragging, startDragging, resetWidth };
};

export default useResizablePanel;

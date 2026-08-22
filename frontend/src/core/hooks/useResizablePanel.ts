import {
  useCallback,
  useEffect,
  useRef,
  useState,
  type KeyboardEvent as ReactKeyboardEvent,
  type PointerEvent as ReactPointerEvent,
} from "react";

type ResizablePanelOptions = {
  /** localStorage key the chosen size is remembered under. */
  storageKey: string;
  defaultSize: number;
  min: number;
  /**
   * A function when the ceiling depends on the viewport or a container measured
   * at drag time (a panel may never grow past its parent), a number when fixed.
   */
  max: number | (() => number);
  axis: "x" | "y";
  /**
   * Set for a panel anchored to the far edge — a bottom panel or a right
   * sidebar — whose size grows as the pointer moves against the axis.
   */
  invert?: boolean;
  /** Pixels a single arrow-key press moves the separator. */
  step?: number;
};

/**
 * A draggable panel size, remembered between sessions.
 *
 * Pointer events are captured on `window` rather than the handle so the drag
 * survives the pointer outracing the separator — at speed the cursor leaves a
 * few-pixel-wide strip long before the layout catches up, and a handler bound
 * to the element itself would drop the gesture mid-drag.
 */
export default function useResizablePanel({
  storageKey,
  defaultSize,
  min,
  max,
  axis,
  invert = false,
  step = 24,
}: ResizablePanelOptions) {
  const [size, setSize] = useState(defaultSize);
  const [isResizing, setIsResizing] = useState(false);
  // The pointer handlers run outside React's render cycle and need the size as
  // of the previous move, which state would only give them a render later.
  const sizeRef = useRef(defaultSize);

  const clamp = useCallback(
    (value: number) =>
      Math.min(Math.max(value, min), typeof max === "function" ? max() : max),
    [min, max],
  );

  const commit = useCallback((value: number) => {
    sizeRef.current = value;
    setSize(value);
  }, []);

  const persist = useCallback(
    (value: number) => {
      try {
        window.localStorage.setItem(storageKey, String(Math.round(value)));
      } catch {
        // A browser with storage disabled or full still resizes, it just will
        // not remember: not worth failing the interaction over.
      }
    },
    [storageKey],
  );

  // Read the remembered size only after mounting. The server has no
  // localStorage, so resolving it during the first render would make the
  // client's markup disagree with the server's and trip hydration.
  useEffect(() => {
    let stored: string | null = null;
    try {
      stored = window.localStorage.getItem(storageKey);
    } catch {
      return;
    }
    if (stored === null) {
      return;
    }
    const parsed = Number(stored);
    if (Number.isFinite(parsed)) {
      commit(clamp(parsed));
    }
  }, [storageKey, clamp, commit]);

  const startResize = useCallback(
    (event: ReactPointerEvent) => {
      // Only the primary button drags; a right-click on the separator should
      // open the context menu as usual.
      if (event.button !== 0) {
        return;
      }
      event.preventDefault();
      const origin = axis === "x" ? event.clientX : event.clientY;
      const originSize = sizeRef.current;
      const ceiling = typeof max === "function" ? max() : max;

      const onMove = (moveEvent: PointerEvent) => {
        const position = axis === "x" ? moveEvent.clientX : moveEvent.clientY;
        const delta = (position - origin) * (invert ? -1 : 1);
        commit(Math.min(Math.max(originSize + delta, min), ceiling));
      };

      const onUp = () => {
        window.removeEventListener("pointermove", onMove);
        window.removeEventListener("pointerup", onUp);
        window.removeEventListener("pointercancel", onUp);
        // Restored rather than cleared outright so a page that sets either of
        // these itself is left as it was.
        document.body.style.userSelect = "";
        document.body.style.cursor = "";
        setIsResizing(false);
        persist(sizeRef.current);
      };

      // Suppress selection and hold the resize cursor for the whole gesture:
      // without this, dragging over the editor selects its text and the cursor
      // flickers as it crosses each child element.
      document.body.style.userSelect = "none";
      document.body.style.cursor = axis === "x" ? "col-resize" : "row-resize";
      setIsResizing(true);
      window.addEventListener("pointermove", onMove);
      window.addEventListener("pointerup", onUp);
      window.addEventListener("pointercancel", onUp);
    },
    [axis, invert, min, max, commit, persist],
  );

  // Arrow keys move the separator too: a pointer drag is unusable without a
  // mouse, and a separator that cannot be reached by keyboard is inaccessible.
  const onKeyDown = useCallback(
    (event: ReactKeyboardEvent) => {
      const forward = axis === "x" ? "ArrowRight" : "ArrowDown";
      const backward = axis === "x" ? "ArrowLeft" : "ArrowUp";
      if (event.key !== forward && event.key !== backward) {
        return;
      }
      event.preventDefault();
      const direction = event.key === forward ? 1 : -1;
      const next = clamp(
        sizeRef.current + direction * step * (invert ? -1 : 1),
      );
      commit(next);
      persist(next);
    },
    [axis, invert, step, clamp, commit, persist],
  );

  return {
    size,
    isResizing,
    /** Spread onto the separator element. */
    separatorProps: {
      role: "separator" as const,
      "aria-orientation": (axis === "x" ? "vertical" : "horizontal") as
        | "vertical"
        | "horizontal",
      "aria-valuenow": Math.round(size),
      tabIndex: 0,
      onPointerDown: startResize,
      onKeyDown,
    },
  };
}

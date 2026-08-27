import {
  ChevronDownIcon,
  ChevronLeftIcon,
  ChevronRightIcon,
  ChevronUpIcon,
} from "@heroicons/react/20/solid";
import clsx from "clsx";
import { useRouter } from "next/router";
import { useTranslation } from "next-i18next";
import useCookieState from "core/hooks/useCookieState";
import {
  panelCookieName,
  sanitizePanelLayout,
  type PanelLayout,
} from "./panelLayout";
import {
  useCallback,
  useEffect,
  useImperativeHandle,
  useLayoutEffect,
  useRef,
  useState,
  type KeyboardEvent as ReactKeyboardEvent,
  type PointerEvent as ReactPointerEvent,
  type ReactNode,
  type Ref,
} from "react";

type Side = "left" | "right" | "top" | "bottom";

type ResizablePanelProps = {
  /** Edge of its container the panel is anchored to; the separator sits opposite. */
  side: Side;
  defaultSize: number;
  minSize: number;
  /** Hard ceiling. Without one the panel may grow to fill its container. */
  maxSize?: number;
  /** Pixels always left to the panel's siblings, measured on the container. */
  reserve?: number;
  /** Dragging past the floor closes the panel entirely; set false to forbid it. */
  collapsible?: boolean;
  /** The panel's name, used to label its separator and collapse toggle. */
  label: string;
  /** Only needed to tell apart two panels on the same side of the same page. */
  id?: string;
  /**
   * Filled with a handle for driving the panel from its owner. A plain prop
   * rather than a `ref`: nothing here forwards to a DOM node, so there is no
   * reason to wrap the component in `forwardRef` for it.
   */
  handleRef?: Ref<ResizablePanelHandle>;
  className?: string;
  children: ReactNode;
};

export type ResizablePanelHandle = {
  /** Reopen the panel if it is closed; a no-op when it is already open. */
  expand(): void;
};

/** Pixels a single arrow-key press moves the separator. */
const STEP = 24;

/** How far below the floor a drag must go before the panel closes instead. */
const COLLAPSE_SLACK = 48;

const isHorizontal = (side: Side) => side === "left" || side === "right";

/**
 * A panel anchored to the far edge grows as the pointer moves against the axis:
 * dragging a right sidebar leftwards makes it wider.
 */
const isInverted = (side: Side) => side === "right" || side === "bottom";

/**
 * The toggle straddles the separator, centred on its length. A closed panel has
 * no width left to straddle, so the button moves off the container's edge and
 * onto the content side — otherwise the card's rounded corners clip half the
 * circle away, and the one control that reopens the panel is the one that gets
 * cut in half.
 */
const togglePosition = (side: Side, collapsed: boolean) => {
  if (isHorizontal(side)) {
    if (!collapsed) {
      return "top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2";
    }
    return side === "left"
      ? "top-1/2 left-1 -translate-y-1/2"
      : "top-1/2 right-1 -translate-y-1/2";
  }
  if (!collapsed) {
    return "top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2";
  }
  return side === "top"
    ? "top-1 left-1/2 -translate-x-1/2"
    : "bottom-1 left-1/2 -translate-x-1/2";
};

/** The toggle points the way the panel will move when it is pressed. */
const chevronFor = (side: Side, collapsed: boolean) => {
  const opening = collapsed !== isInverted(side);
  if (isHorizontal(side)) {
    return opening ? ChevronRightIcon : ChevronLeftIcon;
  }
  return opening ? ChevronDownIcon : ChevronUpIcon;
};

/**
 * The remembered layout belongs to a place in the app, not to a name someone
 * has to invent and keep unique: two panels on one page are already told apart
 * by the side they sit on.
 */
const usePanelName = (side: Side, id?: string) => {
  // The pattern, not the resolved URL — every workspace shares one layout
  // rather than each remembering its own.
  const { pathname } = useRouter();
  return panelCookieName(pathname, id ? `${side}_${id}` : side);
};

// The clamp has to happen before the browser paints, or the panel is visibly
// laid out twice. There is nothing to measure on the server, where React warns
// about layout effects.
const useClampEffect =
  typeof window === "undefined" ? useEffect : useLayoutEffect;

const ResizablePanel = ({
  side,
  defaultSize,
  minSize,
  maxSize,
  reserve = 0,
  collapsible = true,
  label,
  id,
  handleRef,
  className,
  children,
}: ResizablePanelProps) => {
  const { t } = useTranslation();
  const cookieName = usePanelName(side, id);
  // Read while rendering, on the server as much as in the browser: this is what
  // lets the panel come back at its own size without a second layout.
  const [remembered, remember] = useCookieState<PanelLayout>({
    name: cookieName,
    defaultValue: { size: defaultSize, collapsed: false },
  });
  const horizontal = isHorizontal(side);
  const inverted = isInverted(side);

  const panelRef = useRef<HTMLDivElement>(null);
  // The cookie seeds the layout; from then on this is what the panel is sized
  // by, so a drag is not at the mercy of a cookie write.
  const [{ size, collapsed }, setLayout] = useState(() =>
    sanitizePanelLayout(remembered, defaultSize),
  );
  const [isResizing, setIsResizing] = useState(false);
  // The pointer handlers run outside React's render cycle and need the size as
  // of the previous move, which state would only give them a render later.
  const sizeRef = useRef(size);

  const measureMax = useCallback(() => {
    const container = panelRef.current?.parentElement;
    const available = horizontal
      ? container?.clientWidth
      : container?.clientHeight;
    const room = available ? available - reserve : Number.POSITIVE_INFINITY;
    return Math.max(minSize, Math.min(maxSize ?? room, room));
  }, [horizontal, reserve, maxSize, minSize]);

  const clamp = useCallback(
    (value: number) => Math.min(Math.max(value, minSize), measureMax()),
    [minSize, measureMax],
  );

  // The fast path: the panel is sized off this variable, so a drag can move it
  // without going through React at all.
  const paint = useCallback((value: number, isCollapsed: boolean) => {
    // A collapsed panel holds on to the size it will reopen at, so dragging it
    // shut and pulling it back out does not lose the size the user chose.
    if (!isCollapsed) {
      sizeRef.current = value;
    }
    panelRef.current?.style.setProperty(
      "--panel-size",
      `${isCollapsed ? 0 : Math.round(value)}px`,
    );
  }, []);

  const commit = useCallback(
    (value: number, isCollapsed: boolean) => {
      paint(value, isCollapsed);
      setLayout({ size: value, collapsed: isCollapsed });
      remember({ size: Math.round(value), collapsed: isCollapsed });
    },
    [paint, remember],
  );

  // A size chosen in a larger window may not fit this one. Measuring is only
  // possible once there is a container, and only worth doing on the way in: a
  // container that resizes later must not overwrite what the user chose.
  useClampEffect(() => {
    const clamped = clamp(sizeRef.current);
    if (clamped !== sizeRef.current) {
      sizeRef.current = clamped;
      setLayout((layout) => ({ ...layout, size: clamped }));
    }
  }, []);

  const toggleCollapsed = useCallback(() => {
    commit(Math.max(sizeRef.current, minSize), !collapsed);
  }, [commit, collapsed, minSize]);

  useImperativeHandle(
    handleRef,
    () => ({
      expand() {
        if (collapsed) {
          commit(Math.max(sizeRef.current, minSize), false);
        }
      },
    }),
    [handleRef, collapsed, commit, minSize],
  );

  const startResize = useCallback(
    (event: ReactPointerEvent) => {
      // Only the primary button drags; a right-click on the separator should
      // open the context menu as usual.
      if (event.button !== 0) {
        return;
      }
      event.preventDefault();
      const origin = horizontal ? event.clientX : event.clientY;
      // Dragging out of a collapsed panel starts from its closed edge, so the
      // panel follows the pointer instead of jumping to its old size.
      const originSize = collapsed ? 0 : sizeRef.current;
      const ceiling = measureMax();
      let closed = collapsed;

      const onMove = (moveEvent: PointerEvent) => {
        const position = horizontal ? moveEvent.clientX : moveEvent.clientY;
        const delta = (position - origin) * (inverted ? -1 : 1);
        const raw = originSize + delta;
        closed = collapsible && raw < minSize - COLLAPSE_SLACK;
        paint(Math.min(Math.max(raw, minSize), ceiling), closed);
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
        commit(sizeRef.current, closed);
      };

      // Suppress selection and hold the resize cursor for the whole gesture:
      // without this, dragging over the editor selects its text and the cursor
      // flickers as it crosses each child element.
      document.body.style.userSelect = "none";
      document.body.style.cursor = horizontal ? "col-resize" : "row-resize";
      setIsResizing(true);
      window.addEventListener("pointermove", onMove);
      window.addEventListener("pointerup", onUp);
      window.addEventListener("pointercancel", onUp);
    },
    [
      horizontal,
      inverted,
      collapsed,
      collapsible,
      minSize,
      measureMax,
      paint,
      commit,
    ],
  );

  // Arrow keys move the separator too: a pointer drag is unusable without a
  // mouse, and a separator that cannot be reached by keyboard is inaccessible.
  const onKeyDown = useCallback(
    (event: ReactKeyboardEvent) => {
      const grow = horizontal ? "ArrowRight" : "ArrowDown";
      const shrink = horizontal ? "ArrowLeft" : "ArrowUp";
      const towardsPanel = inverted ? shrink : grow;
      const awayFromPanel = inverted ? grow : shrink;
      if (event.key !== towardsPanel && event.key !== awayFromPanel) {
        return;
      }
      event.preventDefault();
      if (collapsed) {
        if (event.key === towardsPanel) {
          commit(Math.max(sizeRef.current, minSize), false);
        }
        return;
      }
      const next =
        sizeRef.current + (event.key === towardsPanel ? STEP : -STEP);
      if (collapsible && next < minSize - COLLAPSE_SLACK) {
        commit(sizeRef.current, true);
        return;
      }
      commit(clamp(next), false);
    },
    [horizontal, inverted, collapsed, collapsible, minSize, clamp, commit],
  );

  const ChevronIcon = chevronFor(side, collapsed);

  const panel = (
    <div
      ref={panelRef}
      // The size is a variable rather than a width so the collapsed state is a
      // pure CSS concern and the panel keeps its own layout rules.
      style={
        {
          "--panel-size": `${collapsed ? 0 : Math.round(size)}px`,
          [horizontal ? "width" : "height"]: "var(--panel-size)",
        } as React.CSSProperties
      }
      className={clsx(
        "shrink-0 overflow-hidden",
        // A remembered size can outlive the window it was chosen in; CSS keeps
        // the panel inside its container without a resize listener.
        horizontal ? "max-w-full" : "max-h-full",
        // Only outside a drag: animating each pointer move would lag the panel
        // behind the cursor.
        !isResizing && "transition-[width,height] duration-150",
        // A closed panel is clipped to nothing already, but its contents would
        // still take focus and be read out; `invisible` takes them out of both.
        collapsed && "invisible",
        className,
      )}
    >
      {children}
    </div>
  );

  const separator = (
    <div
      role="separator"
      aria-orientation={horizontal ? "vertical" : "horizontal"}
      aria-valuenow={collapsed ? 0 : Math.round(size)}
      aria-label={label}
      title={
        collapsible
          ? t("Drag to resize, double-click to collapse")
          : t("Drag to resize")
      }
      tabIndex={0}
      onPointerDown={startResize}
      onKeyDown={onKeyDown}
      onDoubleClick={collapsible ? toggleCollapsed : undefined}
      className={clsx(
        // Lifted above its neighbours so the toggle, which is wider than the
        // strip it sits on, is not painted over by the panels either side.
        "group relative z-10 shrink-0 transition-colors",
        "hover:bg-blue-400 focus-visible:bg-blue-500 focus-visible:outline-none",
        isResizing ? "bg-blue-500" : "bg-gray-200",
        horizontal ? "cursor-col-resize" : "cursor-row-resize",
        // A closed panel leaves nothing but this strip, so it widens into a
        // rail the toggle can sit on and the eye can find.
        collapsed
          ? horizontal
            ? "w-2 bg-gray-100"
            : "h-2 bg-gray-100"
          : horizontal
            ? "w-[2px]"
            : "h-[2px]",
      )}
    >
      {/* Widens the grab area past the visible strip without moving the
          layout, the way an editor gutter behaves. */}
      <span
        className={clsx(
          "absolute",
          horizontal
            ? "inset-y-0 -right-1 -left-1"
            : "inset-x-0 -top-1 -bottom-1",
        )}
      />
      {collapsible && (
        <button
          type="button"
          onClick={toggleCollapsed}
          // The separator below would otherwise read the press as the start of
          // a drag.
          onPointerDown={(event) => event.stopPropagation()}
          aria-label={label}
          aria-expanded={!collapsed}
          title={collapsed ? t("Expand") : t("Collapse")}
          className={clsx(
            "absolute flex h-6 w-6 cursor-pointer items-center justify-center rounded-full border border-gray-300 bg-white text-gray-500 shadow-sm transition hover:border-gray-400 hover:text-gray-800 focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:outline-none",
            togglePosition(side, collapsed),
          )}
        >
          <ChevronIcon className="h-4 w-4" />
        </button>
      )}
    </div>
  );

  return inverted ? (
    <>
      {separator}
      {panel}
    </>
  ) : (
    <>
      {panel}
      {separator}
    </>
  );
};

export default ResizablePanel;

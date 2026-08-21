import { act, renderHook } from "@testing-library/react";
import useResizablePanel from "../useResizablePanel";

const OPTIONS = {
  storageKey: "panel.width",
  defaultSize: 240,
  min: 160,
  max: 640,
  axis: "x" as const,
};

/** A pointerdown on the separator, as React would deliver it. */
const pointerDown = (x: number, y = 0) =>
  ({
    button: 0,
    clientX: x,
    clientY: y,
    preventDefault: () => {},
  }) as unknown as React.PointerEvent;

// jsdom implements no PointerEvent, and the hook only reads clientX/clientY, so
// a MouseEvent carrying the pointer event's type drives the listeners faithfully.
const drag = (to: { x?: number; y?: number }) => {
  window.dispatchEvent(
    new MouseEvent("pointermove", { clientX: to.x ?? 0, clientY: to.y ?? 0 }),
  );
};

const release = () => window.dispatchEvent(new MouseEvent("pointerup"));

const key = (name: string) =>
  ({ key: name, preventDefault: () => {} }) as unknown as React.KeyboardEvent;

describe("useResizablePanel", () => {
  beforeEach(() => {
    window.localStorage.clear();
  });

  it("starts at the default size", () => {
    const { result } = renderHook(() => useResizablePanel(OPTIONS));
    expect(result.current.size).toBe(240);
  });

  it("tracks the pointer while dragging", () => {
    const { result } = renderHook(() => useResizablePanel(OPTIONS));

    act(() => result.current.separatorProps.onPointerDown(pointerDown(500)));
    act(() => drag({ x: 560 }));

    expect(result.current.size).toBe(300);
  });

  it("reports that a resize is in progress, and that it ended", () => {
    const { result } = renderHook(() => useResizablePanel(OPTIONS));
    expect(result.current.isResizing).toBe(false);

    act(() => result.current.separatorProps.onPointerDown(pointerDown(500)));
    expect(result.current.isResizing).toBe(true);

    act(() => release());
    expect(result.current.isResizing).toBe(false);
  });

  it("refuses to shrink past the minimum, so the panel cannot be dragged shut", () => {
    const { result } = renderHook(() => useResizablePanel(OPTIONS));

    act(() => result.current.separatorProps.onPointerDown(pointerDown(500)));
    act(() => drag({ x: 0 }));

    expect(result.current.size).toBe(160);
  });

  it("refuses to grow past the maximum", () => {
    const { result } = renderHook(() => useResizablePanel(OPTIONS));

    act(() => result.current.separatorProps.onPointerDown(pointerDown(500)));
    act(() => drag({ x: 5000 }));

    expect(result.current.size).toBe(640);
  });

  it("evaluates a computed maximum at drag time, not at mount", () => {
    let ceiling = 300;
    const { result } = renderHook(() =>
      useResizablePanel({ ...OPTIONS, max: () => ceiling }),
    );

    ceiling = 400;
    act(() => result.current.separatorProps.onPointerDown(pointerDown(500)));
    act(() => drag({ x: 5000 }));

    expect(result.current.size).toBe(400);
  });

  it("remembers the size only once the drag ends", () => {
    const { result } = renderHook(() => useResizablePanel(OPTIONS));

    act(() => result.current.separatorProps.onPointerDown(pointerDown(500)));
    act(() => drag({ x: 560 }));
    // Writing on every move would hit localStorage dozens of times a second.
    expect(window.localStorage.getItem("panel.width")).toBeNull();

    act(() => release());
    expect(window.localStorage.getItem("panel.width")).toBe("300");
  });

  it("restores a remembered size", () => {
    window.localStorage.setItem("panel.width", "420");
    const { result } = renderHook(() => useResizablePanel(OPTIONS));
    expect(result.current.size).toBe(420);
  });

  it("clamps a remembered size that no longer fits", () => {
    window.localStorage.setItem("panel.width", "9999");
    const { result } = renderHook(() => useResizablePanel(OPTIONS));
    expect(result.current.size).toBe(640);
  });

  it("ignores a corrupt remembered size", () => {
    window.localStorage.setItem("panel.width", "not a number");
    const { result } = renderHook(() => useResizablePanel(OPTIONS));
    expect(result.current.size).toBe(240);
  });

  it("moves on arrow keys, so the separator works without a mouse", () => {
    const { result } = renderHook(() => useResizablePanel(OPTIONS));

    act(() => result.current.separatorProps.onKeyDown(key("ArrowRight")));
    expect(result.current.size).toBe(264);

    act(() => result.current.separatorProps.onKeyDown(key("ArrowLeft")));
    expect(result.current.size).toBe(240);
  });

  it("remembers a keyboard adjustment immediately", () => {
    const { result } = renderHook(() => useResizablePanel(OPTIONS));
    act(() => result.current.separatorProps.onKeyDown(key("ArrowRight")));
    expect(window.localStorage.getItem("panel.width")).toBe("264");
  });

  it("leaves other keys to the browser", () => {
    const { result } = renderHook(() => useResizablePanel(OPTIONS));
    act(() => result.current.separatorProps.onKeyDown(key("Tab")));
    expect(result.current.size).toBe(240);
  });

  it("ignores a non-primary button, leaving the context menu alone", () => {
    const { result } = renderHook(() => useResizablePanel(OPTIONS));

    act(() =>
      result.current.separatorProps.onPointerDown({
        ...pointerDown(500),
        button: 2,
      } as unknown as React.PointerEvent),
    );
    act(() => drag({ x: 560 }));

    expect(result.current.size).toBe(240);
    expect(result.current.isResizing).toBe(false);
  });

  describe("a panel anchored to the far edge", () => {
    const BOTTOM = {
      ...OPTIONS,
      storageKey: "panel.height",
      axis: "y" as const,
      invert: true,
    };

    it("grows as the pointer moves up", () => {
      const { result } = renderHook(() => useResizablePanel(BOTTOM));

      act(() =>
        result.current.separatorProps.onPointerDown(pointerDown(0, 500)),
      );
      act(() => drag({ y: 440 }));

      expect(result.current.size).toBe(300);
    });

    it("grows on ArrowUp, the direction the edge actually moves", () => {
      const { result } = renderHook(() => useResizablePanel(BOTTOM));
      act(() => result.current.separatorProps.onKeyDown(key("ArrowUp")));
      expect(result.current.size).toBe(264);
    });
  });

  describe("accessibility", () => {
    it("exposes a vertical separator for a horizontal drag", () => {
      const { result } = renderHook(() => useResizablePanel(OPTIONS));
      expect(result.current.separatorProps).toMatchObject({
        role: "separator",
        "aria-orientation": "vertical",
        "aria-valuenow": 240,
        tabIndex: 0,
      });
    });

    it("exposes a horizontal separator for a vertical drag", () => {
      const { result } = renderHook(() =>
        useResizablePanel({ ...OPTIONS, axis: "y" }),
      );
      expect(result.current.separatorProps).toMatchObject({
        "aria-orientation": "horizontal",
      });
    });
  });
});

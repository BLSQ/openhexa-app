import { render, screen } from "@testing-library/react";
import { Cookies, CookiesProvider } from "react-cookie";
import { clearCookies } from "core/helpers/testutils";
import userEvent from "@testing-library/user-event";
import { act, createRef } from "react";
import ResizablePanel, { type ResizablePanelHandle } from "./ResizablePanel";

const renderPanel = (
  props: Partial<React.ComponentProps<typeof ResizablePanel>> = {},
) =>
  render(
    <CookiesProvider>
      <div style={{ display: "flex" }}>
        <ResizablePanel
          side="left"
          label="Table list"
          defaultSize={240}
          minSize={160}
          maxSize={640}
          {...props}
        >
          <button>Inside</button>
        </ResizablePanel>
        <div>Rest</div>
      </div>
    </CookiesProvider>,
  );

const separator = () => screen.getByRole("separator");
const panel = () => separator().previousElementSibling as HTMLElement;

// jsdom implements no PointerEvent, and the component only reads
// clientX/clientY, so a MouseEvent carrying the pointer event's type drives the
// window listeners faithfully.
const drag = (from: number, to: number) => {
  act(() => {
    separator().dispatchEvent(
      new MouseEvent("pointerdown", {
        bubbles: true,
        button: 0,
        clientX: from,
      }),
    );
  });
  act(() => {
    window.dispatchEvent(new MouseEvent("pointermove", { clientX: to }));
  });
  act(() => {
    window.dispatchEvent(new MouseEvent("pointerup"));
  });
};

const sizeOf = (element: HTMLElement) =>
  element.style.getPropertyValue("--panel-size");

describe("ResizablePanel", () => {
  beforeEach(clearCookies);

  it("starts at its default size", () => {
    renderPanel();
    expect(sizeOf(panel())).toBe("240px");
    expect(separator()).toHaveAttribute("aria-valuenow", "240");
    expect(separator()).toHaveAttribute("aria-orientation", "vertical");
  });

  it("follows the pointer while dragging", () => {
    renderPanel();
    drag(500, 560);
    expect(sizeOf(panel())).toBe("300px");
  });

  it("keeps the size within its bounds", () => {
    renderPanel({ collapsible: false });
    drag(500, 2000);
    expect(sizeOf(panel())).toBe("640px");

    drag(500, 0);
    expect(sizeOf(panel())).toBe("160px");
  });

  it("collapses when dragged well past the floor, and reopens from the toggle", async () => {
    renderPanel();
    drag(500, 300);

    expect(sizeOf(panel())).toBe("0px");
    expect(panel()).toHaveClass("invisible");
    expect(separator()).toHaveAttribute("aria-valuenow", "0");

    await userEvent.click(screen.getByRole("button", { name: "Table list" }));
    expect(sizeOf(panel())).toBe("240px");
  });

  it("reopens a closed panel when its owner calls expand", () => {
    const ref = createRef<ResizablePanelHandle>();
    renderPanel({ handleRef: ref });
    drag(500, 300);
    expect(sizeOf(panel())).toBe("0px");

    act(() => ref.current?.expand());
    expect(sizeOf(panel())).toBe("240px");
  });

  it("leaves an open panel at its size when expand is called", () => {
    const ref = createRef<ResizablePanelHandle>();
    renderPanel({ handleRef: ref });
    drag(500, 560);
    expect(sizeOf(panel())).toBe("300px");

    act(() => ref.current?.expand());
    expect(sizeOf(panel())).toBe("300px");
  });

  it("does not collapse a panel that forbids it", () => {
    renderPanel({ collapsible: false });
    drag(500, 0);
    expect(sizeOf(panel())).toBe("160px");
    expect(
      screen.queryByRole("button", { name: "Table list" }),
    ).not.toBeInTheDocument();
  });

  it("resizes with the arrow keys, for pointer-free use", async () => {
    renderPanel();
    separator().focus();

    await userEvent.keyboard("{ArrowRight}");
    expect(separator()).toHaveAttribute("aria-valuenow", "264");

    await userEvent.keyboard("{ArrowLeft}{ArrowLeft}");
    expect(separator()).toHaveAttribute("aria-valuenow", "216");
  });

  it("grows a right-anchored panel as the pointer moves left", () => {
    renderPanel({ side: "right" });
    act(() => {
      separator().dispatchEvent(
        new MouseEvent("pointerdown", {
          bubbles: true,
          button: 0,
          clientX: 500,
        }),
      );
    });
    act(() => {
      window.dispatchEvent(new MouseEvent("pointermove", { clientX: 440 }));
    });
    act(() => window.dispatchEvent(new MouseEvent("pointerup")));

    expect(sizeOf(separator().nextElementSibling as HTMLElement)).toBe("300px");
  });

  it("remembers the layout under a cookie named after the route and the side", () => {
    const { unmount } = renderPanel();
    drag(500, 560);

    expect(new Cookies().get("panel___left")).toEqual({
      size: 300,
      collapsed: false,
    });

    unmount();
    renderPanel();
    expect(sizeOf(panel())).toBe("300px");
  });

  it("remembers a collapsed panel", () => {
    const { unmount } = renderPanel();
    drag(500, 300);
    unmount();

    renderPanel();
    expect(sizeOf(panel())).toBe("0px");
    expect(screen.getByRole("button", { name: "Table list" })).toHaveAttribute(
      "aria-expanded",
      "false",
    );
  });

  it("keeps two panels of the same page apart", () => {
    render(
      <CookiesProvider>
        <div style={{ display: "flex", flexDirection: "column" }}>
          <ResizablePanel
            side="top"
            label="Editor"
            defaultSize={260}
            minSize={120}
          >
            <div>Editor</div>
          </ResizablePanel>
          <div>Results</div>
        </div>
      </CookiesProvider>,
    );
    renderPanel();

    expect(screen.getAllByRole("separator")).toHaveLength(2);
    expect(screen.getByRole("separator", { name: "Editor" })).toHaveAttribute(
      "aria-orientation",
      "horizontal",
    );
  });

  it("keeps its toggle within reach whether it is open or closed", () => {
    renderPanel();
    const toggle = screen.getByRole("button", { name: "Table list" });
    expect(toggle).toHaveAttribute("aria-expanded", "true");
    // Not revealed on hover: a control that only exists once the pointer finds
    // the separator is a control most people never find.
    expect(toggle).not.toHaveClass("opacity-0");

    drag(500, 300);
    expect(screen.getByRole("button", { name: "Table list" })).toHaveAttribute(
      "aria-expanded",
      "false",
    );
  });

  it("is already the remembered size in the markup rendered on the server", () => {
    // This is what makes the page load once: the panel is laid out at 380px in
    // the first paint, rather than painting at its default and jumping when
    // React hydrates and reads the cookie.
    // Required inline: react-dom/server needs a TextEncoder, which jsdom does
    // not provide, and the polyfill has to be in place before it loads.
    global.TextEncoder ??= require("util").TextEncoder;
    const { renderToString } = require("react-dom/server");
    new Cookies().set("panel___left", { size: 380, collapsed: false });

    const markup = renderToString(
      <CookiesProvider>
        <ResizablePanel
          side="left"
          label="Table list"
          defaultSize={240}
          minSize={160}
        >
          <div />
        </ResizablePanel>
      </CookiesProvider>,
    );

    expect(markup).toContain("--panel-size:380px");
  });
});

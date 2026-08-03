import { render, waitFor } from "@testing-library/react";
import CodeEditor from "./CodeEditor";

// These tests exercise the real CodeMirror instance (not a textarea stub) so
// that keyboard-shortcut wiring is verified against the editor that actually
// ships. CodeMirror routes key bindings through a `keydown` listener on its
// content DOM, so a binding that returns `true` both fires its handler and
// consumes the event — preventing the default newline insertion.

// jsdom implements neither, and CodeMirror calls them whenever it measures the
// document -- on mount, and after a dispatch that scrolls the cursor into view.
beforeAll(() => {
  Range.prototype.getClientRects = () =>
    Object.assign([], { item: () => null }) as unknown as DOMRectList;
  Range.prototype.getBoundingClientRect = () => new DOMRect();
});

const getContentDOM = async (container: HTMLElement) => {
  const content = await waitFor(() => {
    const el = container.querySelector(".cm-content");
    if (!el) {
      throw new Error("CodeMirror content DOM not mounted yet");
    }
    return el as HTMLElement;
  });
  return content;
};

const dispatchKeyDown = (
  target: HTMLElement,
  init: KeyboardEventInit,
): KeyboardEvent => {
  const event = new KeyboardEvent("keydown", {
    bubbles: true,
    cancelable: true,
    ...init,
  });
  target.dispatchEvent(event);
  return event;
};

const dispatchPaste = (target: HTMLElement, text: string): Event => {
  // jsdom has no ClipboardEvent constructor with a working clipboardData.
  const event = new Event("paste", { bubbles: true, cancelable: true });
  Object.defineProperty(event, "clipboardData", {
    value: { getData: () => text },
  });
  target.dispatchEvent(event);
  return event;
};

describe("CodeEditor paste sanitisation", () => {
  it("rewrites the pasted text through the injected sanitiser", async () => {
    const onChange = jest.fn();
    const { container } = render(
      <CodeEditor
        lang="sql"
        value=""
        onChange={onChange}
        sanitizeInsertedText={(text) => text.replace(/\u00a0/g, " ")}
      />,
    );

    const content = await getContentDOM(container);
    dispatchPaste(content, "SELECT\u00a01");

    // CodeMirror reports the value alongside a ViewUpdate; only the text matters.
    await waitFor(() => expect(onChange.mock.calls[0]?.[0]).toBe("SELECT 1"));
  });

  it("inserts the text unchanged when there is nothing to rewrite", async () => {
    const onChange = jest.fn();
    const { container } = render(
      <CodeEditor
        lang="sql"
        value=""
        onChange={onChange}
        sanitizeInsertedText={(text) => text}
      />,
    );

    const content = await getContentDOM(container);
    dispatchPaste(content, "SELECT 1");

    await waitFor(() => expect(onChange.mock.calls[0]?.[0]).toBe("SELECT 1"));
  });
});

describe("CodeEditor shortcuts", () => {
  it("fires and consumes the shortcut on Ctrl+Enter", async () => {
    const run = jest.fn();
    const { container } = render(
      <CodeEditor
        lang="sql"
        value="SELECT 1"
        shortcuts={[{ key: "Mod-Enter", run }]}
      />,
    );

    const content = await getContentDOM(container);
    const event = dispatchKeyDown(content, { key: "Enter", ctrlKey: true });

    expect(run).toHaveBeenCalledTimes(1);
    // A handled binding preventing default is what stops the newline from being
    // inserted; the old wrapper-div bubble handler could not achieve this.
    expect(event.defaultPrevented).toBe(true);
  });

  it("fires and consumes the shortcut on Cmd+Enter", async () => {
    // jsdom reports a non-mac platform, where "Mod" resolves to Ctrl; bind the
    // Cmd spec explicitly to verify the meta-modifier path fires and is consumed
    // (this is what "Mod-Enter" maps to for real macOS users).
    const run = jest.fn();
    const { container } = render(
      <CodeEditor
        lang="sql"
        value="SELECT 1"
        shortcuts={[{ key: "Cmd-Enter", run }]}
      />,
    );

    const content = await getContentDOM(container);
    const event = dispatchKeyDown(content, { key: "Enter", metaKey: true });

    expect(run).toHaveBeenCalledTimes(1);
    expect(event.defaultPrevented).toBe(true);
  });

  it("does not fire the shortcut for a plain Enter", async () => {
    const run = jest.fn();
    const { container } = render(
      <CodeEditor
        lang="sql"
        value="SELECT 1"
        shortcuts={[{ key: "Mod-Enter", run }]}
      />,
    );

    const content = await getContentDOM(container);
    dispatchKeyDown(content, { key: "Enter" });

    expect(run).not.toHaveBeenCalled();
  });
});

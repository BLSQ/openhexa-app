import { act, render, waitFor } from "@testing-library/react";
import { createRef } from "react";
import CodeEditor, { CodeEditorHandle } from "./CodeEditor";

// These tests exercise the real CodeMirror instance (not a textarea stub) so
// that keyboard-shortcut wiring is verified against the editor that actually
// ships. CodeMirror routes key bindings through a `keydown` listener on its
// content DOM, so a binding that returns `true` both fires its handler and
// consumes the event — preventing the default newline insertion.

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

  it("fires and consumes the shortcut on Ctrl/Cmd+F", async () => {
    const run = jest.fn();
    const { container } = render(
      <CodeEditor
        lang="sql"
        value="SELECT 1"
        shortcuts={[{ key: "Mod-f", run }]}
      />,
    );

    const content = await getContentDOM(container);
    const event = dispatchKeyDown(content, { key: "f", ctrlKey: true });

    expect(run).toHaveBeenCalledTimes(1);
    // Consuming the event is what keeps the browser's find bar closed.
    expect(event.defaultPrevented).toBe(true);
    // …and it must beat basicSetup's own Mod-f binding, not merely run beside
    // it: the search panel stays shut.
    expect(container.querySelector(".cm-search")).toBeNull();
  });

  it("fires the shortcut on Shift+Alt+F", async () => {
    const run = jest.fn();
    const { container } = render(
      <CodeEditor
        lang="sql"
        value="SELECT 1"
        shortcuts={[{ key: "Shift-Alt-f", run }]}
      />,
    );

    const content = await getContentDOM(container);
    dispatchKeyDown(content, {
      key: "F",
      altKey: true,
      shiftKey: true,
      keyCode: 70,
    });

    expect(run).toHaveBeenCalledTimes(1);
  });
});

describe("CodeEditor search panel", () => {
  it("moves search to Mod-Shift-f when a shortcut claims Mod-f", async () => {
    const { container } = render(
      <CodeEditor
        lang="sql"
        value="SELECT 1"
        shortcuts={[{ key: "Mod-f", run: jest.fn() }]}
      />,
    );

    const content = await getContentDOM(container);
    // A real Ctrl+Shift+F reports the shifted character and a keyCode; without
    // both, CodeMirror resolves the event to "Ctrl-f" and never reaches the
    // Shift binding.
    dispatchKeyDown(content, {
      key: "F",
      ctrlKey: true,
      shiftKey: true,
      keyCode: 70,
    });

    expect(container.querySelector(".cm-search")).not.toBeNull();
  });

  it("leaves search on its native Mod-f when nothing claims the key", async () => {
    const { container } = render(<CodeEditor lang="sql" value="SELECT 1" />);

    const content = await getContentDOM(container);
    dispatchKeyDown(content, { key: "f", ctrlKey: true });

    expect(container.querySelector(".cm-search")).not.toBeNull();
  });
});

describe("CodeEditor handle", () => {
  it("replaces the document and reports the new text", async () => {
    const onChange = jest.fn();
    const ref = createRef<CodeEditorHandle>();
    const { container } = render(
      <CodeEditor ref={ref} lang="sql" value="select 1" onChange={onChange} />,
    );
    await getContentDOM(container);

    act(() => ref.current?.replaceAll("SELECT\n  1"));

    expect(onChange.mock.calls[0][0]).toEqual("SELECT\n  1");
  });

  it("keeps the replacement undoable", async () => {
    const ref = createRef<CodeEditorHandle>();
    const { container } = render(
      <CodeEditor ref={ref} lang="sql" value="select 1" />,
    );
    const content = await getContentDOM(container);

    act(() => ref.current?.replaceAll("SELECT\n  1"));
    // Formatting must not be a one-way door: the pre-format text is still one
    // undo away.
    dispatchKeyDown(content, { key: "z", ctrlKey: true });

    expect(content.textContent).toEqual("select 1");
  });
});

import { fireEvent, renderHook } from "@testing-library/react";
import useSaveShortcut from "../useSaveShortcut";

const onSave = jest.fn();

const press = (init: KeyboardEventInit) =>
  // fireEvent returns false when a handler called preventDefault — i.e. the
  // browser's own "Save page as…" dialog will not open.
  fireEvent.keyDown(window, init);

beforeEach(() => {
  onSave.mockClear();
});

describe("useSaveShortcut", () => {
  it.each([
    ["Cmd+S", { key: "s", metaKey: true }],
    ["Ctrl+S", { key: "s", ctrlKey: true }],
  ])("saves on %s and consumes the keystroke", (_label, init) => {
    renderHook(() => useSaveShortcut(onSave));

    expect(press(init)).toBe(false);
    expect(onSave).toHaveBeenCalledTimes(1);
  });

  it.each([
    ["a bare s", { key: "s" }],
    ["another modified key", { key: "d", metaKey: true }],
    ["Cmd+Shift+S", { key: "s", metaKey: true, shiftKey: true }],
    ["Ctrl+Alt+S", { key: "s", ctrlKey: true, altKey: true }],
  ])("ignores %s", (_label, init) => {
    renderHook(() => useSaveShortcut(onSave));

    expect(press(init)).toBe(true);
    expect(onSave).not.toHaveBeenCalled();
  });

  it("consumes auto-repeats of a held key without saving again", () => {
    renderHook(() => useSaveShortcut(onSave));

    expect(press({ key: "s", metaKey: true })).toBe(false);
    // Still swallowed, or holding the key would pop the browser's save dialog.
    expect(press({ key: "s", metaKey: true, repeat: true })).toBe(false);
    expect(press({ key: "s", metaKey: true, repeat: true })).toBe(false);

    expect(onSave).toHaveBeenCalledTimes(1);
  });

  it("calls the latest callback without resubscribing", () => {
    const later = jest.fn();
    const { rerender } = renderHook(({ handler }) => useSaveShortcut(handler), {
      initialProps: { handler: onSave },
    });

    rerender({ handler: later });
    press({ key: "s", metaKey: true });

    expect(onSave).not.toHaveBeenCalled();
    expect(later).toHaveBeenCalledTimes(1);
  });

  it("stops listening once unmounted", () => {
    const { unmount } = renderHook(() => useSaveShortcut(onSave));
    unmount();

    press({ key: "s", metaKey: true });
    expect(onSave).not.toHaveBeenCalled();
  });
});

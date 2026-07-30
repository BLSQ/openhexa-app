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

  it("does not save when disabled, and leaves the keystroke to the browser", () => {
    renderHook(() => useSaveShortcut(onSave, false));

    expect(press({ key: "s", metaKey: true })).toBe(true);
    expect(onSave).not.toHaveBeenCalled();
  });

  it("stops listening once unmounted", () => {
    const { unmount } = renderHook(() => useSaveShortcut(onSave));
    unmount();

    press({ key: "s", metaKey: true });
    expect(onSave).not.toHaveBeenCalled();
  });
});

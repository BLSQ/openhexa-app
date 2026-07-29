import { act, renderHook } from "@testing-library/react";
import { useQueryBuffer } from "./useQueryBuffer";

const STORAGE_KEY = "user-data.data-studio.scratch.user-1.ws-1";

const storedDraft = () => window.localStorage.getItem(STORAGE_KEY);

const renderBuffer = (savedQuery?: { content: string } | null) =>
  renderHook(() =>
    useQueryBuffer({ userId: "user-1", workspaceSlug: "ws-1", savedQuery }),
  );

// Edits are mirrored on a debounce, so tests drive the clock rather than wait.
const settle = () => act(() => jest.advanceTimersByTime(1_000));

beforeEach(() => {
  jest.useFakeTimers();
});

afterEach(() => {
  jest.useRealTimers();
});

describe("useQueryBuffer", () => {
  it("starts empty when there is nothing to restore", () => {
    const { result } = renderBuffer();

    expect(result.current[0]).toBe("");
  });

  it("restores the scratch draft of the workspace", () => {
    window.localStorage.setItem(STORAGE_KEY, "SELECT 1");

    const { result } = renderBuffer();

    expect(result.current[0]).toBe("SELECT 1");
  });

  it("ignores a draft belonging to another user", () => {
    window.localStorage.setItem(
      "user-data.data-studio.scratch.user-2.ws-1",
      "SELECT 1",
    );

    const { result } = renderBuffer();

    expect(result.current[0]).toBe("");
  });

  it("leaves the draft alone until the user edits", () => {
    window.localStorage.setItem(STORAGE_KEY, "SELECT 1");

    renderBuffer();
    settle();

    expect(storedDraft()).toBe("SELECT 1");
  });

  it("mirrors edits to the scratch draft", () => {
    const { result } = renderBuffer();

    act(() => result.current[1]("SELECT 2"));
    settle();

    expect(result.current[0]).toBe("SELECT 2");
    expect(storedDraft()).toBe("SELECT 2");
  });

  it("writes once for a burst of keystrokes rather than once each", () => {
    const setItem = jest.spyOn(Storage.prototype, "setItem");
    const { result } = renderBuffer();

    act(() => result.current[1]("S"));
    act(() => result.current[1]("SE"));
    act(() => result.current[1]("SEL"));

    expect(setItem).not.toHaveBeenCalled();

    settle();

    expect(setItem).toHaveBeenCalledTimes(1);
    expect(storedDraft()).toBe("SEL");
  });

  it("flushes a pending draft when the tab is hidden", () => {
    const { result } = renderBuffer();

    act(() => result.current[1]("SELECT 2"));
    act(() => {
      window.dispatchEvent(new Event("pagehide"));
    });

    expect(storedDraft()).toBe("SELECT 2");
  });

  it("flushes a pending draft when the page is backgrounded", () => {
    const { result } = renderBuffer();

    act(() => result.current[1]("SELECT 2"));
    jest.spyOn(document, "visibilityState", "get").mockReturnValue("hidden");
    act(() => {
      document.dispatchEvent(new Event("visibilitychange"));
    });

    expect(storedDraft()).toBe("SELECT 2");
  });

  it("keeps the draft while the page is merely revealed", () => {
    const setItem = jest.spyOn(Storage.prototype, "setItem");
    const { result } = renderBuffer();

    act(() => result.current[1]("SELECT 2"));
    act(() => {
      document.dispatchEvent(new Event("visibilitychange"));
    });

    expect(setItem).not.toHaveBeenCalled();
  });

  it("flushes a pending draft when the editor unmounts", () => {
    const { result, unmount } = renderBuffer();

    act(() => result.current[1]("SELECT 2"));
    unmount();

    expect(storedDraft()).toBe("SELECT 2");
  });

  it("drops the draft when the user empties the editor", () => {
    window.localStorage.setItem(STORAGE_KEY, "SELECT 1");
    const { result } = renderBuffer();

    act(() => result.current[1](""));
    settle();

    expect(storedDraft()).toBeNull();
  });

  it("starts from the content of a saved query", () => {
    const { result } = renderBuffer({ content: "SELECT 3" });

    expect(result.current[0]).toBe("SELECT 3");
  });

  it("does not mirror the buffer of a saved query", () => {
    window.localStorage.setItem(STORAGE_KEY, "SELECT 1");
    const { result } = renderBuffer({ content: "SELECT 3" });

    act(() => result.current[1]("SELECT 4"));
    settle();

    expect(result.current[0]).toBe("SELECT 4");
    expect(storedDraft()).toBe("SELECT 1");
  });
});

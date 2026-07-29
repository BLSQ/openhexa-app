import { act, renderHook } from "@testing-library/react";
import { useQueryBuffer } from "./useQueryBuffer";

const STORAGE_KEY = "data-studio.scratch.ws-1";

const storedDraft = () => window.localStorage.getItem(STORAGE_KEY);

const renderBuffer = (savedQuery?: { content: string } | null) =>
  renderHook(() => useQueryBuffer({ workspaceSlug: "ws-1", savedQuery }));

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

  it("leaves the draft alone until the user edits", () => {
    window.localStorage.setItem(STORAGE_KEY, "SELECT 1");

    renderBuffer();

    expect(storedDraft()).toBe("SELECT 1");
  });

  it("mirrors edits to the scratch draft", () => {
    const { result } = renderBuffer();

    act(() => result.current[1]("SELECT 2"));

    expect(result.current[0]).toBe("SELECT 2");
    expect(storedDraft()).toBe("SELECT 2");
  });

  it("drops the draft when the user empties the editor", () => {
    window.localStorage.setItem(STORAGE_KEY, "SELECT 1");
    const { result } = renderBuffer();

    act(() => result.current[1](""));

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

    expect(result.current[0]).toBe("SELECT 4");
    expect(storedDraft()).toBe("SELECT 1");
  });
});

import { act, renderHook } from "@testing-library/react";
import useWordDrain from "./useWordDrain";

jest.useFakeTimers();

describe("useWordDrain", () => {
  it("returns the full fed text when flushed mid-drain", () => {
    const { result } = renderHook(() => useWordDrain({ interval: 30 }));

    act(() => {
      result.current.feed("Let me search the database for");
    });
    act(() => {
      jest.advanceTimersByTime(60);
    });

    let captured = "";
    act(() => {
      captured = result.current.flush();
    });

    expect(captured).toBe("Let me search the database for");
  });

  it("reveals a stranded trailing word once the stream stalls", () => {
    const { result } = renderHook(() => useWordDrain({ interval: 30 }));

    act(() => {
      result.current.feed("Looking that up");
    });
    // Drain the words that have a whitespace boundary; the final word "up" has
    // no trailing space and would otherwise stay hidden until done().
    act(() => {
      jest.advanceTimersByTime(90);
    });
    expect(result.current.text).toBe("Looking that ");
    expect(result.current.pending).toBe(true);

    // After the idle grace period the trailing word is revealed.
    act(() => {
      jest.advanceTimersByTime(120);
    });
    expect(result.current.text).toBe("Looking that up");
    expect(result.current.pending).toBe(false);
  });

  it("tracks pending while text is queued and clears once caught up", () => {
    const { result } = renderHook(() => useWordDrain({ interval: 30 }));

    expect(result.current.pending).toBe(false);

    act(() => {
      result.current.feed("Hello world ");
    });
    expect(result.current.pending).toBe(true);

    act(() => {
      jest.advanceTimersByTime(120);
    });
    expect(result.current.text).toBe("Hello world ");
    expect(result.current.pending).toBe(false);
  });
});

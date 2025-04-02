import useLocalStorage from "../useLocalStorage";
import { renderHook, waitFor } from "@testing-library/react";

describe("useLocalStorage", () => {
  it("returns an empty value for a non-existent key", () => {
    const { result } = renderHook(() => useLocalStorage("key", "value"));
    expect(result.current[0]).toBe("value");
  });

  it("returns the value for an existing key", () => {
    window.localStorage.setItem("key", JSON.stringify("other_value"));
    const { result } = renderHook(() => useLocalStorage("key", "value"));
    expect(result.current[0]).toBe("other_value");
  });

  it("returns the default value for an invalid value", () => {
    window.localStorage.setItem("key", "invalid value '(not json)'");
    const { result } = renderHook(() => useLocalStorage("key", "value"));
    expect(result.current[0]).toBe("value");
  });

  it("sets the value passed", async () => {
    const { result, rerender } = renderHook(() =>
      useLocalStorage("key", "value"),
    );

    const [value, setValue] = result.current;
    await waitFor(() => setValue("new_value"));
    await waitFor(() => {
      expect(result.current[0]).toBe("new_value");
    });
  });
});

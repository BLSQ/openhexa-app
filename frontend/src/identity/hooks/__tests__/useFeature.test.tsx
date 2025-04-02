import { renderHook } from "@testing-library/react";
import useFeature from "../useFeature";

const FEATURES = [
  { code: "a_feature", config: {} },
  { code: "b_feature", config: { specialConfig: "xyz" } },
];

const mockMe = jest.fn(() => ({
  features: FEATURES,
}));

jest.mock("identity/hooks/useMe", () => () => mockMe());

describe("useFeature", () => {
  it("returns false for an unknown feature", async () => {
    const { result } = renderHook((props) => useFeature(props.code), {
      initialProps: { code: "unknown" },
    });
    expect(result.current).toEqual([false, null]);
  });
  it("returns the feature and its config", async () => {
    const { result } = renderHook(() => useFeature("b_feature"));
    expect(result.current).toEqual([true, { specialConfig: "xyz" }]);
  });
  it("returns the new feature if the code changes on render", async () => {
    const { result, rerender } = renderHook((props) => useFeature(props.code), {
      initialProps: { code: "unknown" },
    });

    expect(result.current).toEqual([false, null]);

    rerender({ code: "a_feature" });
    expect(result.current).toEqual([true, {}]);

    rerender({ code: "b_feature" });
    expect(result.current).toEqual([true, { specialConfig: "xyz" }]);
  });
});

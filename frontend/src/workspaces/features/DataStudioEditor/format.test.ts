import { stringifyCellValue } from "./format";

describe("stringifyCellValue", () => {
  it("renders null and undefined as an empty string", () => {
    expect(stringifyCellValue(null)).toBe("");
    expect(stringifyCellValue(undefined)).toBe("");
  });

  it("serialises objects and arrays as JSON", () => {
    expect(stringifyCellValue({ x: 1 })).toBe('{"x":1}');
    expect(stringifyCellValue([1, "a"])).toBe('[1,"a"]');
  });

  it("stringifies primitives", () => {
    expect(stringifyCellValue(42)).toBe("42");
    expect(stringifyCellValue(0)).toBe("0");
    expect(stringifyCellValue(true)).toBe("true");
    expect(stringifyCellValue(false)).toBe("false");
    expect(stringifyCellValue("hello")).toBe("hello");
  });
});

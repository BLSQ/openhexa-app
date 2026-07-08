import { isNumericValue, stringifyCellValue } from "./format";

describe("isNumericValue", () => {
  it("treats JS numbers as numeric", () => {
    expect(isNumericValue(42)).toBe(true);
    expect(isNumericValue(-5.5)).toBe(true);
    expect(isNumericValue(0)).toBe(true);
  });

  it("treats numeric strings as numeric (NUMERIC/DECIMAL arrive as strings)", () => {
    for (const value of [
      "-5.5",
      "-5",
      "0",
      "-0",
      "0.5",
      ".5",
      "5.",
      "1e10",
      "-1.5e-3",
    ]) {
      expect(isNumericValue(value)).toBe(true);
    }
  });

  it("rejects strings that only start like a number", () => {
    for (const value of [
      "+1",
      "-cmd",
      "-1+1",
      "-5abc",
      "-",
      "-1e",
      "1,2",
      "$5",
      "",
    ]) {
      expect(isNumericValue(value)).toBe(false);
    }
  });

  it("rejects non-number, non-string values", () => {
    expect(isNumericValue(null)).toBe(false);
    expect(isNumericValue(undefined)).toBe(false);
    expect(isNumericValue(true)).toBe(false);
    expect(isNumericValue({ x: 1 })).toBe(false);
  });
});

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

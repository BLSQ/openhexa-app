import { ensureArray } from "../array";

describe("Array", () => {
  it("returns an empty array when input is undefined", () => {
    expect(ensureArray(undefined)).toEqual([]);
  });
  it("returns an empty array when input is null", () => {
    expect(ensureArray(null)).toEqual([]);
  });
  it("returns the same input when it's an array", () => {
    const values = [1, 2, 3];
    expect(ensureArray(values)).toHaveLength(3);
    expect(ensureArray(values)).toEqual(values);
  });
  it("returns an array that contains the passed value", () => {
    const v1 = 1;
    const v2 = { one: 1, two: 2 };
    expect(ensureArray(v1)).toEqual([v1]);
    expect(ensureArray(v2)).toEqual([{ one: 1, two: 2 }]);
  });
});

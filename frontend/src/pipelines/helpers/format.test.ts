import { ParameterType } from "graphql/types";
import { formatParamValue } from "./format";

const base = {
  code: "p",
  name: "P",
  multiple: false,
  required: false,
};

describe("formatParamValue", () => {
  it("returns ✓ for a true bool", () => {
    expect(
      formatParamValue({ ...base, type: ParameterType.Bool, value: true }),
    ).toBe("✓");
  });

  it("returns ✗ for a false bool", () => {
    expect(
      formatParamValue({ ...base, type: ParameterType.Bool, value: false }),
    ).toBe("✗");
  });

  it("returns masked value for a non-empty secret", () => {
    expect(
      formatParamValue({
        ...base,
        type: ParameterType.Secret,
        value: "s3cr3t",
      }),
    ).toBe("••••••");
  });

  it("returns '-' for an empty secret", () => {
    expect(
      formatParamValue({ ...base, type: ParameterType.Secret, value: "" }),
    ).toBe("-");
  });

  it("returns '-' for a null value", () => {
    expect(
      formatParamValue({ ...base, type: ParameterType.Str, value: null }),
    ).toBe("-");
  });

  it("returns '-' for an undefined value", () => {
    expect(
      formatParamValue({ ...base, type: ParameterType.Str, value: undefined }),
    ).toBe("-");
  });

  it("joins array values with ', ' when multiple is true", () => {
    expect(
      formatParamValue({
        ...base,
        type: ParameterType.Str,
        multiple: true,
        value: ["a", "b", "c"],
      }),
    ).toBe("a, b, c");
  });

  it("returns string representation for a plain string value", () => {
    expect(
      formatParamValue({ ...base, type: ParameterType.Str, value: "hello" }),
    ).toBe("hello");
  });

  it("returns string representation for a numeric int value", () => {
    expect(
      formatParamValue({ ...base, type: ParameterType.Int, value: 42 }),
    ).toBe("42");
  });

  it("returns string representation for a float value", () => {
    expect(
      formatParamValue({ ...base, type: ParameterType.Float, value: 3.14 }),
    ).toBe("3.14");
  });

  it("returns string representation for a connection parameter", () => {
    expect(
      formatParamValue({
        ...base,
        type: ParameterType.Postgresql,
        value: "my-conn-slug",
      }),
    ).toBe("my-conn-slug");
  });
});

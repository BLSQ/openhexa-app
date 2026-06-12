import {
  convertParametersToPipelineInput,
  getDisabledParameterCodes,
  getParameterDisablers,
} from "./pipelines";

const parameters = [
  {
    code: "run_report_only",
    type: "bool",
    multiple: false,
    disables: ["data_input", "year"],
  },
  { code: "data_input", type: "str", multiple: false },
  { code: "year", type: "int", multiple: false },
  { code: "report_name", type: "str", multiple: false },
];

describe("getDisabledParameterCodes", () => {
  it("returns no disabled codes when the controller is off", () => {
    const disabled = getDisabledParameterCodes(parameters, {
      run_report_only: false,
    });
    expect(disabled.size).toBe(0);
  });

  it("disables the listed parameters when the controller is on", () => {
    const disabled = getDisabledParameterCodes(parameters, {
      run_report_only: true,
    });
    expect(Array.from(disabled).sort()).toEqual(["data_input", "year"]);
  });

  it("unions the targets of several active controllers", () => {
    const params = [
      { code: "toggle_a", type: "bool", multiple: false, disables: ["x"] },
      { code: "toggle_b", type: "bool", multiple: false, disables: ["x", "y"] },
      { code: "x", type: "str", multiple: false },
      { code: "y", type: "str", multiple: false },
    ];
    const disabled = getDisabledParameterCodes(params, {
      toggle_a: true,
      toggle_b: true,
    });
    expect(Array.from(disabled).sort()).toEqual(["x", "y"]);
  });

  it("disables when off for disableWhen=false (enable toggle)", () => {
    const params = [
      {
        code: "enable_advanced",
        type: "bool",
        multiple: false,
        disables: ["tuning"],
        disableWhen: false,
      },
      { code: "tuning", type: "str", multiple: false },
    ];
    expect(
      Array.from(getDisabledParameterCodes(params, { enable_advanced: false })),
    ).toEqual(["tuning"]);
    expect(
      getDisabledParameterCodes(params, { enable_advanced: true }).size,
    ).toBe(0);
  });
});

describe("getParameterDisablers", () => {
  it("lists each controller once even if it repeats a target in `disables`", () => {
    const params = [
      {
        code: "skip_coffee",
        type: "bool",
        multiple: false,
        disables: ["coffee_int", "coffee_choices", "coffee_int"],
      },
      { code: "coffee_int", type: "int", multiple: false },
      { code: "coffee_choices", type: "str", multiple: false },
    ];
    const disablers = getParameterDisablers(params, { skip_coffee: true });
    expect(disablers.get("coffee_int")).toEqual(["skip_coffee"]);
    expect(disablers.get("coffee_choices")).toEqual(["skip_coffee"]);
  });

  it("lists every distinct controller disabling the same target", () => {
    const params = [
      { code: "toggle_a", type: "bool", multiple: false, disables: ["x"] },
      { code: "toggle_b", type: "bool", multiple: false, disables: ["x"] },
      { code: "x", type: "str", multiple: false },
    ];
    const disablers = getParameterDisablers(params, {
      toggle_a: true,
      toggle_b: true,
    });
    expect(disablers.get("x")).toEqual(["toggle_a", "toggle_b"]);
  });
});

describe("convertParametersToPipelineInput with disables", () => {
  it("omits disabled parameters (and ignores their dummy values)", () => {
    const config = convertParametersToPipelineInput(
      { parameters },
      {
        run_report_only: true,
        data_input: "dummy",
        year: 1,
        report_name: "Q1",
      },
    );
    expect(config).toEqual({
      run_report_only: true,
      report_name: "Q1",
    });
  });

  it("keeps all parameters when the controller is off", () => {
    const config = convertParametersToPipelineInput(
      { parameters },
      {
        run_report_only: false,
        data_input: "real",
        year: 2024,
        report_name: "Q1",
      },
    );
    expect(config).toEqual({
      run_report_only: false,
      data_input: "real",
      year: 2024,
      report_name: "Q1",
    });
  });
});

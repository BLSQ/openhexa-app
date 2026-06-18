import { getToolConfig } from "./toolConfig";

// Tests pin the literal tool-name contract (the string the backend sends) rather
// than reusing the TOOL constant, so a wrong rename is caught instead of passing
// tautologically.
describe("getToolConfig", () => {
  it("hides the output and relabels the input for propose_pipeline_version", () => {
    const config = getToolConfig("propose_pipeline_version");
    expect(config.hideOutput).toBe(true);
    expect(config.inputLabel).toBe("Proposed changes");
  });

  it("returns an empty config for tools without overrides", () => {
    expect(getToolConfig("get_workspace")).toEqual({});
    expect(getToolConfig("list_files").hideOutput).toBeUndefined();
  });
});

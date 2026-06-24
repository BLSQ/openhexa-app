import type { TFunction } from "i18next";
import { getToolConfig } from "./toolConfig";

// Identity translator so the test reads back the literal i18n key the thunk
// resolves, without pulling in i18next.
const identityT = ((key: string) => key) as unknown as TFunction;

// Tests pin the literal tool-name contract (the string the backend sends) rather
// than reusing the TOOL constant, so a wrong rename is caught instead of passing
// no matter what.
describe("getToolConfig", () => {
  it("hides the output and relabels the input for propose_pipeline_version", () => {
    const config = getToolConfig("propose_pipeline_version");
    expect(config.hideOutput).toBe(true);
    expect(config.inputLabel?.(identityT)).toBe("Proposed changes");
  });

  it("returns an empty config for tools without overrides", () => {
    expect(getToolConfig("get_workspace")).toEqual({});
    expect(getToolConfig("list_files").hideOutput).toBeUndefined();
  });
});

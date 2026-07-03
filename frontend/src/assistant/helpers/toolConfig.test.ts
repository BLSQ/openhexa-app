import type { TFunction } from "i18next";
import { TOOL } from "assistant/helpers/tools";
import { getToolConfig } from "./toolConfig";

// Identity translator so the test reads back the literal i18n key the thunk
// resolves, without pulling in i18next.
const identityT = ((key: string) => key) as unknown as TFunction;

describe("getToolConfig", () => {
  it("hides the output and relabels the input for propose_pipeline_version", () => {
    const config = getToolConfig(TOOL.ProposePipelineVersion);
    expect(config.hideOutput).toBe(true);
    expect(config.inputLabel?.(identityT)).toBe("Proposed changes");
  });

  it("returns an empty config for tools without overrides", () => {
    expect(getToolConfig(TOOL.ListFiles)).toEqual({});
    expect(getToolConfig(TOOL.ReadFile).hideOutput).toBeUndefined();
  });

  it("returns an empty config for an unknown tool (null)", () => {
    expect(getToolConfig(null)).toEqual({});
  });
});

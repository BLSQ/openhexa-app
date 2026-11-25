import { isAiAvailable } from "./helpers";

describe("isAiAvailable", () => {
  const workspace = (aiEnabled: boolean, organizationEnabled: boolean) => ({
    aiEnabled,
    organization: { aiSettings: { enabled: organizationEnabled } },
  });

  it("is available when the organization and the workspace allow AI", () => {
    expect(isAiAvailable(workspace(true, true))).toBe(true);
  });

  it("is unavailable when the workspace admins disabled AI", () => {
    expect(isAiAvailable(workspace(false, true))).toBe(false);
  });

  it("is unavailable when the organization has not enabled AI", () => {
    expect(isAiAvailable(workspace(true, false))).toBe(false);
  });

  it("is unavailable while the workspace is not loaded", () => {
    expect(isAiAvailable(undefined)).toBe(false);
  });
});

import { formatPlanName } from "./organization";

describe("formatPlanName", () => {
  it.each([
    ["openhexa_starter", "Starter"],
    ["openhexa_pro", "Pro"],
    ["openhexa_enterprise_plus", "Enterprise Plus"],
    ["custom_plan", "Custom Plan"],
  ])("formats %s as %s", (planCode, expected) => {
    expect(formatPlanName(planCode)).toBe(expected);
  });
});

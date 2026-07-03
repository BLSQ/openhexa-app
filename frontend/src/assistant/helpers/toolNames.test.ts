import type { TFunction } from "i18next";
import { AssistantToolName } from "graphql/types";
import { getToolLabels } from "./toolNames";

// Identity translator so labels read back as their literal i18n key without
// pulling in i18next.
const identityT = ((key: string) => key) as unknown as TFunction;

describe("getToolLabels", () => {
  // Every agent-reachable tool must have a curated, translatable label. The
  // `formatToolName` fallback returns raw English (never passed through `t`), so
  // a tool that reaches the chat UI without an entry here would render
  // untranslated. `AssistantToolName` is the exact reachable set (generated from
  // the agent registry), so this fails the moment a new tool is added without a
  // label — turning a silent i18n gap into a red test.
  it("has a label for every tool in AssistantToolName", () => {
    const labels = getToolLabels(identityT);
    const missing = Object.values(AssistantToolName).filter(
      (name) => !labels[name],
    );
    expect(missing).toEqual([]);
  });
});

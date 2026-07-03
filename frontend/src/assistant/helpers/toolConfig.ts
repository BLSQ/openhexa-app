import type { TFunction } from "i18next";
import { AssistantToolName } from "graphql/types";
import { TOOL } from "assistant/helpers/tools";

// Per-tool UI behavior. This intentionally holds only knowledge that is keyed to
// a specific tool name; shape-based presentation (tables, JSON, …) stays in the
// renderer registry, which matches on data shape rather than tool name.
type ToolUiConfig = {
  // propose_pipeline_version's output is the full materialized version (every
  // preserved file merged with the edits) and is already reviewable in the
  // FilesEditor diff, so re-rendering it in the card is redundant noise. The
  // meaningful artifact is the input changeset (modified/deleted files).
  hideOutput?: boolean;
  // Override the generic "Input" header when that word would mislead — e.g. the
  // changeset is the agent's *proposed change*, not a function argument. Given
  // as a translator thunk so the i18n key stays a literal `t("…")` call the
  // parser can extract, co-located with the config (no separate label→t() map).
  inputLabel?: (t: TFunction) => string;
};

const TOOL_CONFIG: Partial<Record<AssistantToolName, ToolUiConfig>> = {
  [TOOL.ProposePipelineVersion]: {
    hideOutput: true,
    inputLabel: (t) => t("Proposed changes"),
  },
};

export function getToolConfig(tool: AssistantToolName | null): ToolUiConfig {
  return (tool && TOOL_CONFIG[tool]) || {};
}

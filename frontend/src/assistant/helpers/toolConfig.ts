import { TOOL } from "assistant/helpers/tools";

// Per-tool UI behavior. This intentionally holds only knowledge that is keyed to
// a specific tool name; shape-based presentation (tables, JSON, …) stays in the
// renderer registry, which matches on data shape rather than tool name.
export type ToolInputLabel = "Proposed changes";

type ToolUiConfig = {
  // propose_pipeline_version's output is the full materialized version (every
  // preserved file merged with the edits) and is already reviewable in the
  // FilesEditor diff, so re-rendering it in the card is redundant noise. The
  // meaningful artifact is the input changeset (modified/deleted files).
  hideOutput?: boolean;
  // Override the generic "Input" header when that word would mislead — e.g. the
  // changeset is the agent's *proposed change*, not a function argument.
  inputLabel?: ToolInputLabel;
};

const TOOL_CONFIG: Record<string, ToolUiConfig> = {
  [TOOL.PROPOSE_PIPELINE_VERSION]: {
    hideOutput: true,
    inputLabel: "Proposed changes",
  },
};

export function getToolConfig(name: string): ToolUiConfig {
  return TOOL_CONFIG[name] ?? {};
}

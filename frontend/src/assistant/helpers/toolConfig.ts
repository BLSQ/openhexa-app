import { TOOL } from "assistant/helpers/tools";

// Per-tool UI behavior. This intentionally holds only knowledge that is keyed to
// a specific tool name; shape-based presentation (tables, JSON, …) stays in the
// renderer registry, which matches on data shape rather than tool name.
type ToolUiConfig = {
  // The tool's input merely restates its output (e.g. propose_pipeline_version
  // echoes the proposed file content back in its result), so showing the input
  // section would be redundant noise.
  hideInput?: boolean;
};

const TOOL_CONFIG: Record<string, ToolUiConfig> = {
  [TOOL.PROPOSE_PIPELINE_VERSION]: { hideInput: true },
};

export function getToolConfig(name: string): ToolUiConfig {
  return TOOL_CONFIG[name] ?? {};
}

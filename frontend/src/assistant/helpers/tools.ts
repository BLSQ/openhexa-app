import { AssistantToolName } from "graphql/types";

// Canonical roster of assistant tool machine names. `AssistantToolName` is the
// codegen-emitted enum declared in `hexa/assistant/graphql/schema.graphql`; a
// backend test keeps its members in sync with the agent registry (every tool any
// agent can call). This alias just gives the assistant UI a conventional name to
// key its label, config, and renderer tables off.
export const TOOL = AssistantToolName;

export type ToolName = AssistantToolName;

const TOOL_NAMES = new Set<string>(Object.values(AssistantToolName));

// Typed view of a raw tool name string — the same coercion the backend applies to
// resolve `AssistantToolSegment.tool`. Used on the live SSE path, where segments
// arrive as plain strings (no GraphQL), so history and streaming resolve `tool`
// identically. Null for an unknown/removed tool or a missing name.
export function coerceTool(
  toolName: string | null | undefined,
): AssistantToolName | null {
  return toolName && TOOL_NAMES.has(toolName)
    ? (toolName as AssistantToolName)
    : null;
}

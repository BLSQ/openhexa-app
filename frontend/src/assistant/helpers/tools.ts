import { AssistantToolName } from "graphql/types";

// Canonical roster of assistant tool machine names. `AssistantToolName` is the
// codegen-emitted enum declared in `hexa/assistant/graphql/schema.graphql`; a
// backend test keeps its members in sync with the agent registry (every tool any
// agent can call). This alias just gives the assistant UI a conventional name to
// key its label, config, and renderer tables off.
export const TOOL = AssistantToolName;

export type ToolName = AssistantToolName;

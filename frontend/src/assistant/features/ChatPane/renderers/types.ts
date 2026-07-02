import type { TFunction } from "i18next";
import { ReactNode } from "react";
import { AssistantToolName } from "graphql/types";

export type ToolValueKind = "input" | "output";

// The full invocation is exposed so a renderer can read its sibling value
// (e.g. the code renderer derives a language from the input's file path while
// rendering the output content).
export type RenderContext = {
  kind: ToolValueKind;
  // Typed tool identity — what renderers match on. Null for an unknown/removed
  // tool; `toolName` still carries the raw name for display in that case.
  tool: AssistantToolName | null;
  toolName: string;
  success: boolean;
  input: unknown;
  output: unknown;
};

// A semantic renderer offers a prettier alternative to raw JSON for a value it
// recognizes. `match` lets it decline so resolution falls through to the next
// candidate (and ultimately to the raw JSON view).
export type SemanticRenderer = {
  id: string;
  // The "formatted" toggle label, given as a translator thunk so the i18n key
  // lives here as a literal `t("…")` call the parser can extract — see the note
  // in renderers/index.tsx.
  label: (t: TFunction) => string;
  // Hint that this view benefits from more horizontal/vertical room (e.g. wide
  // tables): the section gives it a taller inline preview and a wider modal.
  wide?: boolean;
  match: (value: unknown, ctx: RenderContext) => boolean;
  render: (value: unknown, ctx: RenderContext) => ReactNode;
};

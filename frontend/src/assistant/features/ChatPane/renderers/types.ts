import { ReactNode } from "react";

export type ToolValueKind = "input" | "output";

// The full invocation is exposed so a renderer can read its sibling value
// (e.g. the code renderer derives a language from the input's file path while
// rendering the output content).
export type RenderContext = {
  kind: ToolValueKind;
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
  // i18n key for the "formatted" toggle label.
  label: string;
  match: (value: unknown, ctx: RenderContext) => boolean;
  render: (value: unknown, ctx: RenderContext) => ReactNode;
};

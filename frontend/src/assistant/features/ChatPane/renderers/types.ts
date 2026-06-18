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

// The "formatted" toggle label of a renderer. A closed union (rather than a bare
// string) so a new renderer is forced to register a translation in
// `getRendererLabel` — the type won't compile otherwise.
export type RendererLabel = "Files" | "Code" | "Document" | "Table";

// A semantic renderer offers a prettier alternative to raw JSON for a value it
// recognizes. `match` lets it decline so resolution falls through to the next
// candidate (and ultimately to the raw JSON view).
export type SemanticRenderer = {
  id: string;
  // i18n key for the "formatted" toggle label.
  label: RendererLabel;
  // Hint that this view benefits from more horizontal/vertical room (e.g. wide
  // tables): the section gives it a taller inline preview and a wider modal.
  wide?: boolean;
  match: (value: unknown, ctx: RenderContext) => boolean;
  render: (value: unknown, ctx: RenderContext) => ReactNode;
};

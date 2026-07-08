import { HighlightStyle } from "@codemirror/language";
import { EditorView } from "@codemirror/view";
import { tags } from "@lezer/highlight";

// Editor-only syntax colors, mirrored from Tailwind's palette (CodeMirror can't
// use utility classes). These are the editor's own design decisions, not shared
// app tokens. Keywords reuse the shared brand accent (see `--color-brand-*` in
// globals.css) so the editor tracks any rebrand automatically.
const colors = {
  emerald: { 700: "#047857" },
  amber: { 700: "#b45309" },
  violet: { 600: "#7c3aed" },
  gray: { 300: "#d1d5db", 400: "#9ca3af", 500: "#6b7280" },
} as const;

export const embeddedHighlightStyle = HighlightStyle.define([
  { tag: tags.keyword, color: "var(--color-brand-strong)", fontWeight: "500" },
  { tag: [tags.string, tags.special(tags.string)], color: colors.emerald[700] },
  { tag: [tags.number, tags.bool, tags.null], color: colors.amber[700] },
  { tag: tags.comment, color: colors.gray[400], fontStyle: "italic" },
  { tag: [tags.operator, tags.punctuation], color: colors.gray[500] },
  {
    tag: [tags.function(tags.variableName), tags.labelName],
    color: colors.violet[600],
  },
]);

// Fill the whole pane so clicking any blank space places the cursor (textarea
// feel), and give the line-number gutter a flat light-gray look.
export const embeddedEditorTheme = EditorView.theme({
  "&": { height: "100%" },
  ".cm-scroller": { minHeight: "100%" },
  ".cm-content": { minHeight: "100%" },
  ".cm-gutters": {
    backgroundColor: "transparent",
    border: "none",
    color: colors.gray[300],
  },
  ".cm-lineNumbers .cm-gutterElement": { padding: "0 1rem 0 1.25rem" },
  ".cm-activeLineGutter": {
    backgroundColor: "transparent",
    color: colors.gray[400],
  },
  "&.cm-focused .cm-activeLine": { backgroundColor: "rgba(21, 93, 251, 0.03)" },
  ".cm-activeLine": { backgroundColor: "transparent" },
  // Suppress CodeMirror's default focus outline (1px dotted #212121). The focus
  // indicator is the wrapper border in CodeEditor.tsx; an outline here would be
  // clipped on the right by the pane's `overflow-hidden`.
  "&.cm-editor.cm-focused": { outline: "none" },
});

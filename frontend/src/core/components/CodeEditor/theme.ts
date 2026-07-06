import { HighlightStyle } from "@codemirror/language";
import { EditorView } from "@codemirror/view";
import { tags } from "@lezer/highlight";

import { colors } from "core/helpers/colors";

// Design-system syntax palette: pink keywords, emerald strings, amber numbers.
// Colors come from the shared brand palette so the editor stays in sync with the
// Tailwind utility classes used elsewhere (e.g. the `pink-500` brand accent).
export const embeddedHighlightStyle = HighlightStyle.define([
  { tag: tags.keyword, color: colors.pink[600], fontWeight: "500" },
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

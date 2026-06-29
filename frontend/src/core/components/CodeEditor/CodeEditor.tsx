import { HighlightStyle, syntaxHighlighting } from "@codemirror/language";
import { json } from "@codemirror/lang-json";
import { python } from "@codemirror/lang-python";
import { sql } from "@codemirror/lang-sql";
import { xml } from "@codemirror/lang-xml";
import { yaml } from "@codemirror/lang-yaml";
import { EditorView } from "@codemirror/view";
import { tags } from "@lezer/highlight";
import CodeMirror, { ReactCodeMirrorRef } from "@uiw/react-codemirror";
import clsx from "clsx";
import { forwardRef, useImperativeHandle, useMemo, useRef } from "react";

// Design-system syntax palette: pink keywords, emerald strings, amber numbers.
// Shared default for the embedded look; split into its own prop if a consumer
// ever needs the embedded layout with different colors.
const embeddedHighlightStyle = HighlightStyle.define([
  { tag: tags.keyword, color: "#db2777", fontWeight: "500" },
  { tag: [tags.string, tags.special(tags.string)], color: "#047857" },
  { tag: [tags.number, tags.bool, tags.null], color: "#b45309" },
  { tag: tags.comment, color: "#9ca3af", fontStyle: "italic" },
  { tag: [tags.operator, tags.punctuation], color: "#6b7280" },
  { tag: [tags.function(tags.variableName), tags.labelName], color: "#7c3aed" },
]);

// Fill the whole pane so clicking any blank space places the cursor (textarea
// feel), and give the line-number gutter a flat light-gray look.
const embeddedEditorTheme = EditorView.theme({
  "&": { height: "100%" },
  ".cm-scroller": { minHeight: "100%" },
  ".cm-content": { minHeight: "100%" },
  ".cm-gutters": {
    backgroundColor: "transparent",
    border: "none",
    color: "#d1d5db",
  },
  ".cm-lineNumbers .cm-gutterElement": { padding: "0 1rem 0 1.25rem" },
  ".cm-activeLineGutter": { backgroundColor: "transparent", color: "#9ca3af" },
  "&.cm-focused .cm-activeLine": { backgroundColor: "rgba(21, 93, 251, 0.03)" },
  ".cm-activeLine": { backgroundColor: "transparent" },
});

type CodeEditorProps = {
  value?: string;
  onChange?(value: string): void;
  readonly?: boolean;
  editable?: boolean;
  minHeight?: string;
  height?: string;
  lang?: "json" | "python" | "xml" | "yaml" | "sql" | string;
  placeholder?: string;
  /** Render as a flush, full-height editing surface (no border, focus ring, themed syntax). */
  embedded?: boolean;
  className?: string;
};

export type CodeEditorHandle = {
  /** Insert text at the current cursor position (replacing any selection). */
  insertText(text: string): void;
  /** The currently selected text, or an empty string when nothing is selected. */
  getSelectedText(): string;
};

const CodeEditor = forwardRef<CodeEditorHandle, CodeEditorProps>(
  (props, ref) => {
    const {
      value,
      readonly,
      editable = true,
      height,
      lang,
      minHeight = "200px",
      onChange,
      placeholder,
      embedded = false,
      className,
    } = props;

    const cmRef = useRef<ReactCodeMirrorRef>(null);

    useImperativeHandle(ref, () => ({
      insertText(text: string) {
        const view = cmRef.current?.view;
        if (!view) {
          return;
        }
        const { from, to } = view.state.selection.main;
        view.dispatch({
          changes: { from, to, insert: text },
          selection: { anchor: from + text.length },
        });
        view.focus();
      },
      getSelectedText() {
        const view = cmRef.current?.view;
        if (!view) {
          return "";
        }
        const { from, to } = view.state.selection.main;
        return view.state.sliceDoc(from, to);
      },
    }));

    const extensions = useMemo(() => {
      const langExtension = (() => {
        switch (lang) {
          case "json":
            return [json()];
          case "python":
            return [python()];
          case "xml":
            return [xml()];
          case "yaml":
            return [yaml()];
          case "sql":
            return [sql()];
          default:
            return [];
        }
      })();
      return embedded
        ? [
            ...langExtension,
            syntaxHighlighting(embeddedHighlightStyle),
            embeddedEditorTheme,
          ]
        : langExtension;
    }, [lang, embedded]);

    return (
      <div
        className={clsx(
          embedded
            ? // Let the @uiw root + editor fill the pane so any click is writable.
              "[&>div]:h-full focus-within:border-blue-500/40 focus-within:ring-1 focus-within:ring-blue-500/20"
            : "overflow-y-auto rounded-md border",
          className,
        )}
      >
        <CodeMirror
          ref={cmRef}
          readOnly={readonly}
          editable={editable}
          height={height}
          minHeight={minHeight}
          placeholder={placeholder}
          extensions={extensions}
          value={value}
          onChange={onChange}
        />
      </div>
    );
  },
);

CodeEditor.displayName = "CodeEditor";

export default CodeEditor;

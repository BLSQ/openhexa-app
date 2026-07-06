import { syntaxHighlighting } from "@codemirror/language";
import { json } from "@codemirror/lang-json";
import { python } from "@codemirror/lang-python";
import { PostgreSQL, sql } from "@codemirror/lang-sql";
import { xml } from "@codemirror/lang-xml";
import { yaml } from "@codemirror/lang-yaml";
import CodeMirror, { ReactCodeMirrorRef } from "@uiw/react-codemirror";
import clsx from "clsx";
import { forwardRef, useImperativeHandle, useMemo, useRef } from "react";

import { embeddedEditorTheme, embeddedHighlightStyle } from "./theme";

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
  /** Focus the editor on mount. */
  autoFocus?: boolean;
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
      autoFocus = false,
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
            // Workspace databases are PostgreSQL, so use its dialect to
            // highlight Postgres-only keywords (EXPLAIN, ANALYZE, VACUUM, …)
            // that the default ANSI dialect does not recognise.
            return [sql({ dialect: PostgreSQL })];
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
              // Focus indicator: a border-box border on this wrapper (transparent
              // until focus). Unlike an outset `ring` or CodeMirror's own
              // `outline`, a border stays inside the element's box, so it is not
              // clipped on the right by the pane's `overflow-hidden`, and it sits
              // outside the editor's scrollbars. CodeMirror's default outline is
              // suppressed in `embeddedEditorTheme` so it does not add a
              // right-clipped line of its own.
              "[&>div]:h-full border border-transparent focus-within:border-blue-300/80"
            : "overflow-y-auto rounded-md border",
          className,
        )}
      >
        <CodeMirror
          ref={cmRef}
          readOnly={readonly}
          editable={editable}
          autoFocus={autoFocus}
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

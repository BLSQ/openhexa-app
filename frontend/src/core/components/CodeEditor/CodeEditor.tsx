import { syntaxHighlighting } from "@codemirror/language";
import { json } from "@codemirror/lang-json";
import { python } from "@codemirror/lang-python";
import { PostgreSQL, SQLNamespace, sql } from "@codemirror/lang-sql";
import { xml } from "@codemirror/lang-xml";
import { yaml } from "@codemirror/lang-yaml";
import CodeMirror, {
  Prec,
  ReactCodeMirrorRef,
  keymap,
} from "@uiw/react-codemirror";
import clsx from "clsx";
import { forwardRef, useImperativeHandle, useMemo, useRef } from "react";

import { embeddedEditorTheme, embeddedHighlightStyle } from "./theme";

/** A keyboard shortcut handled inside the editor. */
export type CodeEditorShortcut = {
  /**
   * A CodeMirror key spec, e.g. "Mod-Enter" ("Mod" is Cmd on macOS, Ctrl
   * elsewhere). See https://codemirror.net/docs/ref/#view.KeyBinding.key
   */
  key: string;
  run(): void;
};

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
  /**
   * Keyboard shortcuts bound inside the editor. Handled at CodeMirror's keymap
   * level (not a bubbling DOM listener), so the keystroke is consumed and its
   * default action — e.g. inserting a newline on Enter — is suppressed.
   */
  shortcuts?: CodeEditorShortcut[];
  className?: string;
  /** Table/column metadata for `lang="sql"` autocomplete (`sql()`'s `schema` option). */
  sqlSchema?: SQLNamespace;
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
      shortcuts,
      className,
      sqlSchema,
    } = props;

    const cmRef = useRef<ReactCodeMirrorRef>(null);

    // Hold the latest handlers in a ref so the memoised keymap always calls the
    // current callback without being reconfigured on every render.
    const shortcutsRef = useRef(shortcuts);
    shortcutsRef.current = shortcuts;

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

    // Rebuild only when the set of keys changes; the callbacks come from the
    // ref, so a shortcut whose handler closes over fresh state stays current.
    const shortcutKeys = (shortcuts ?? []).map((s) => s.key).join("\n");
    const shortcutExtension = useMemo(() => {
      const keys = shortcutKeys ? shortcutKeys.split("\n") : [];
      return Prec.highest(
        keymap.of(
          keys.map((key, index) => ({
            key,
            preventDefault: true,
            run: () => {
              shortcutsRef.current?.[index]?.run();
              return true;
            },
          })),
        ),
      );
    }, [shortcutKeys]);

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
            // that the default ANSI dialect does not recognise. Passing
            // `schema` plugs real table/column names into the same
            // `autocompletion()` popup (from @uiw/react-codemirror's default
            // basicSetup) and also resolves table aliases automatically.
            return [sql({ dialect: PostgreSQL, schema: sqlSchema })];
          default:
            return [];
        }
      })();
      const base = embedded
        ? [
            ...langExtension,
            syntaxHighlighting(embeddedHighlightStyle),
            embeddedEditorTheme,
          ]
        : langExtension;
      return [...base, shortcutExtension];
    }, [lang, embedded, shortcutExtension, sqlSchema]);

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

import { json } from "@codemirror/lang-json";
import { python } from "@codemirror/lang-python";
import { sql } from "@codemirror/lang-sql";
import { xml } from "@codemirror/lang-xml";
import { yaml } from "@codemirror/lang-yaml";
import CodeMirror, { ReactCodeMirrorRef } from "@uiw/react-codemirror";
import clsx from "clsx";
import { forwardRef, useImperativeHandle, useMemo, useRef } from "react";
type CodeEditorProps = {
  value?: string;
  onChange?(value: string): void;
  readonly?: boolean;
  editable?: boolean;
  minHeight?: string;
  height?: string;
  lang?: "json" | "python" | "xml" | "yaml" | "sql" | string;
  className?: string;
};

export type CodeEditorHandle = {
  /** Insert text at the current cursor position (replacing any selection). */
  insertText(text: string): void;
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
    }));

    const extensions = useMemo(() => {
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
    }, [lang]);

    return (
      <div className={clsx("overflow-y-auto rounded-md border", className)}>
        <CodeMirror
          ref={cmRef}
          readOnly={readonly}
          editable={editable}
          height={height}
          minHeight={minHeight}
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

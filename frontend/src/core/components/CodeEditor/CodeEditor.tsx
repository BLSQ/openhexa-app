import { json } from "@codemirror/lang-json";
import { python } from "@codemirror/lang-python";
import CodeMirror from "@uiw/react-codemirror";
import clsx from "clsx";
import { useMemo } from "react";
type CodeEditorProps = {
  value?: string;
  onChange?(value: string): void;
  readonly?: boolean;
  editable?: boolean;
  minHeight?: string;
  height?: string;
  lang?: "json" | "python" | string;
  className?: string;
};

function CodeEditor(props: CodeEditorProps) {
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

  const extensions = useMemo(() => {
    switch (lang) {
      case "json":
        return [json()];
      case "python":
        return [python()];
      default:
        return [];
    }
  }, [lang]);

  return (
    <div className={clsx("overflow-y-auto rounded-md border", className)}>
      <CodeMirror
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
}

export default CodeEditor;

import { json } from "@codemirror/lang-json";
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
  lang?: "json";
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
    if (lang === "json") {
      return [json()];
    }
  }, [lang]);

  return (
    <div
      className={clsx("max-h-44 overflow-y-auto rounded-md border", className)}
    >
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

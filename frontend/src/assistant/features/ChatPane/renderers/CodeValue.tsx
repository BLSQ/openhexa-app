import SyntaxHighlighter from "react-syntax-highlighter";
import { github } from "react-syntax-highlighter/dist/esm/styles/hljs";

const EXTENSION_LANGUAGES: Record<string, string> = {
  py: "python",
  js: "javascript",
  jsx: "javascript",
  ts: "typescript",
  tsx: "typescript",
  json: "json",
  ipynb: "json",
  sql: "sql",
  sh: "bash",
  bash: "bash",
  yaml: "yaml",
  yml: "yaml",
  md: "markdown",
  html: "xml",
  xml: "xml",
  css: "css",
  r: "r",
  toml: "ini",
  ini: "ini",
};

function languageFor(fileName?: string): string {
  if (!fileName) return "text";
  const ext = fileName.split(".").pop()?.toLowerCase() ?? "";
  return EXTENSION_LANGUAGES[ext] ?? "text";
}

type Props = {
  content: string;
  fileName?: string;
};

export default function CodeValue({ content, fileName }: Props) {
  return (
    <SyntaxHighlighter
      language={languageFor(fileName)}
      style={github}
      wrapLongLines
      customStyle={{
        margin: 0,
        borderRadius: "0.375rem",
        fontSize: "0.75rem",
        background: "#ffffff",
        border: "1px solid #e5e7eb",
        padding: "0.625rem 0.75rem",
        whiteSpace: "pre-wrap",
        wordBreak: "break-word",
      }}
    >
      {content}
    </SyntaxHighlighter>
  );
}

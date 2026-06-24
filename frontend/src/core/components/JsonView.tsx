import clsx from "clsx";
import SyntaxHighlighter from "react-syntax-highlighter";
import { github } from "react-syntax-highlighter/dist/esm/styles/hljs";
import { useMemo } from "react";
import Clipboard from "core/components/Clipboard";
import { CODE_BLOCK_STYLE } from "core/components/codeBlockStyle";

type Props = {
  value: unknown;
  className?: string;
  // Cap the rendered height; content scrolls past it. Pass null to render at full
  // height (e.g. when an outer container already handles truncation/scrolling).
  maxHeight?: number | null;
  // Hide the built-in copy button when an outer container already provides one.
  hideCopy?: boolean;
};

function stringify(value: unknown): string {
  if (typeof value === "string") return value;
  try {
    return JSON.stringify(value, null, 2);
  } catch {
    return String(value);
  }
}

export default function JsonView({
  value,
  className,
  maxHeight = 320,
  hideCopy = false,
}: Props) {
  // A raw string output (e.g. a non-JSON tool result) reads better as plain text
  // than as a quoted JSON scalar, so only highlight when it is structured data.
  const isStructured = typeof value === "object" && value !== null;
  const text = useMemo(() => stringify(value), [value]);
  const capped = maxHeight != null;

  return (
    <div className={clsx("group relative", className)}>
      {!hideCopy && (
        <div className="absolute right-1.5 top-1.5 z-10 opacity-0 transition-opacity group-hover:opacity-100">
          <Clipboard value={text} iconClassName="h-3.5 w-3.5 text-gray-400" />
        </div>
      )}
      <div
        className={capped ? "overflow-y-auto" : undefined}
        style={capped ? { maxHeight } : undefined}
      >
        {isStructured ? (
          <SyntaxHighlighter
            language="json"
            style={github}
            wrapLongLines
            customStyle={CODE_BLOCK_STYLE}
          >
            {text}
          </SyntaxHighlighter>
        ) : (
          <pre className="m-0 whitespace-pre-wrap break-words rounded-md border border-gray-200 bg-white px-3 py-2.5 font-mono text-xs text-gray-800">
            {text}
          </pre>
        )}
      </div>
    </div>
  );
}

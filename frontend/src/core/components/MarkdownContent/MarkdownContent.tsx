import clsx from "clsx";
import ReactMarkdown, { type Components } from "react-markdown";
import SyntaxHighlighter from "react-syntax-highlighter";
import { github } from "react-syntax-highlighter/dist/esm/styles/hljs";
import remarkGfm from "remark-gfm";
import { useMemo } from "react";

const REMARK_PLUGINS = [remarkGfm];

type Props = {
  children: string;
  className?: string;
  sm?: boolean;
};

export default function MarkdownContent({ children, className, sm }: Props) {
  const components: Components = useMemo(
    () => ({
      pre: ({ children }) => <>{children}</>,
      code: ({ className: codeClassName, children }) => {
        const match = /language-(\w+)/.exec(codeClassName || "");
        const content = String(children);
        const isBlock = content.endsWith("\n");

        if (isBlock) {
          return (
            <div className="not-prose my-3">
              <SyntaxHighlighter
                language={match?.[1] ?? "text"}
                style={github}
                customStyle={{
                  borderRadius: "0.375rem",
                  fontSize: sm ? "0.75rem" : "0.875rem",
                  background: "#ffffff",
                  border: "1px solid #e5e7eb",
                }}
              >
                {content.replace(/\n$/, "")}
              </SyntaxHighlighter>
            </div>
          );
        }

        return (
          <code className="not-prose bg-gray-200 text-gray-800 rounded px-1.5 py-0.5 font-mono text-[0.875em]">
            {children}
          </code>
        );
      },
    }),
    [sm],
  );

  return (
    <div
      className={clsx(
        "prose max-w-none",
        "prose-headings:font-medium prose-h1:font-medium",
        sm && "prose-sm prose-h1:text-xl prose-h2:text-lg prose-h3:text-md",
        className,
      )}
    >
      <ReactMarkdown remarkPlugins={REMARK_PLUGINS} components={components}>
        {children}
      </ReactMarkdown>
    </div>
  );
}

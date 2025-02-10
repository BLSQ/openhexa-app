import clsx from "clsx";
import React, { useMemo } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import Link from "../Link";

type MarkdownViewerProps = {
  children: string;
  maxWidth?: string;
  className?: string;
  sm?: boolean;
};

const MarkdownViewer = (props: MarkdownViewerProps) => {
  const { children, maxWidth = "max-w-3xl", className, sm = false } = props;

  const components = useMemo<
    React.ComponentProps<typeof ReactMarkdown>["components"]
  >(
    () => ({
      a: ({ node, ...props }) => (
        <Link noStyle href={props.href || ""}>
          {props.children}
        </Link>
      ),
      ul: ({ node, ...props }) => (
        <ul className="list-disc">{props.children}</ul>
      ),
    }),
    [],
  );
  return (
    <ReactMarkdown
      remarkPlugins={[remarkGfm]}
      className={clsx(
        "prose prose-headings:font-medium prose-h1:font-medium",
        maxWidth,
        className,
        sm &&
          "prose-sm prose-h1:text-xl prose-h2:text-lg prose-h3:text-md prose-h2:mt-0",
      )}
      components={components}
    >
      {children}
    </ReactMarkdown>
  );
};

export default MarkdownViewer;

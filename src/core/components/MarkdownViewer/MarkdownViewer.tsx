import clsx from "clsx";
import React, { useMemo } from "react";
import ReactMarkdown from "react-markdown";
import Link from "../Link";

type MarkdownViewerProps = {
  children: string;
  maxWidth?: string;
  className?: string;
};

const MarkdownViewer = (props: MarkdownViewerProps) => {
  const { children, maxWidth = "max-w-3xl", className } = props;

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
    []
  );
  return (
    <ReactMarkdown
      className={clsx("prose prose-headings:font-medium", maxWidth, className)}
      components={components}
    >
      {children}
    </ReactMarkdown>
  );
};

export default MarkdownViewer;

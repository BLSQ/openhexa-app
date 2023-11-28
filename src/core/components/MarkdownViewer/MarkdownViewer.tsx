import clsx from "clsx";
import React, { useMemo } from "react";
import ReactMarkdown from "react-markdown";
import Link from "../Link";
import remarkGfm from "remark-gfm";

type MarkdownViewerProps = {
  children: string;
  maxWidth?: string;
  className?: string;
  allowedElements?: string[];
};

const MarkdownViewer = (props: MarkdownViewerProps) => {
  const {
    children,
    maxWidth = "max-w-3xl",
    className,
    allowedElements,
  } = props;

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
      className={clsx("prose prose-headings:font-medium", maxWidth, className)}
      components={components}
      remarkPlugins={[remarkGfm]}
      allowedElements={allowedElements}
    >
      {children}
    </ReactMarkdown>
  );
};

export default MarkdownViewer;

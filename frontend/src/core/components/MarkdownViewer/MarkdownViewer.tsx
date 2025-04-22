import React from "react";
import MarkdownEditor from "../MarkdownEditor";
import type { MarkdownEditorProps } from "../MarkdownEditor/MarkdownEditor";

export type MarkdownViewerProps = Omit<MarkdownEditorProps, "readOnly">;

const MarkdownViewer = (props: MarkdownViewerProps) => {
  return <MarkdownEditor {...props} readOnly />;
};

export default MarkdownViewer;

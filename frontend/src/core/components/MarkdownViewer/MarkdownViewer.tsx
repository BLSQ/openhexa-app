import React from "react";
import MarkdownEditor, {
  MarkdownEditorProps,
} from "../MarkdownEditor/MarkdownEditor";

export type MarkdownViewerProps = Omit<MarkdownEditorProps, "readOnly">;

const MarkdownViewer = (props: MarkdownViewerProps) => {
  return <MarkdownEditor {...props} readOnly />;
};

export default MarkdownViewer;

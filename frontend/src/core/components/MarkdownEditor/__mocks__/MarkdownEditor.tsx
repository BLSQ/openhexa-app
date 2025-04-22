import Textarea from "core/components/forms/Textarea";

type MarkdownEditorMockProps = {
  markdown: string;
  onChange?: (markdown: string) => void;
  readOnly?: boolean;
  id?: string;
};

const MarkdownEditorMock = (props: MarkdownEditorMockProps) => {
  return (
    <Textarea
      id={props.id}
      readOnly={props.readOnly}
      value={props.markdown}
      onChange={(e) => (props.onChange ? props.onChange(e.target.value) : null)}
    />
  );
};

export default MarkdownEditorMock;

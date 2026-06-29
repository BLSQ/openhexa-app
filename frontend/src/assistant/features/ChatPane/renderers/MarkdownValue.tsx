import MarkdownContent from "core/components/MarkdownContent";

export default function MarkdownValue({ content }: { content: string }) {
  return <MarkdownContent sm>{content}</MarkdownContent>;
}

import MarkdownViewer from "core/components/MarkdownViewer";
import { useEffect, useRef, useState } from "react";
import { useTranslation } from "next-i18next";

const MAX_HEIGHT = 200;

type CollapsibleMarkdownProps = {
  content: string;
};

const CollapsibleMarkdown = ({ content }: CollapsibleMarkdownProps) => {
  const { t } = useTranslation();
  const [expanded, setExpanded] = useState(false);
  const [overflows, setOverflows] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (ref.current) {
      setOverflows(ref.current.scrollHeight > MAX_HEIGHT);
    }
  }, [content]);

  return (
    <div>
      <div
        ref={ref}
        className="overflow-hidden"
        style={!expanded ? { maxHeight: MAX_HEIGHT } : undefined}
      >
        <MarkdownViewer sm markdown={content} />
      </div>
      {overflows && (
        <button
          className="mt-1 text-sm text-blue-600 hover:underline"
          onClick={() => setExpanded(!expanded)}
        >
          {expanded ? t("Show less") : t("Show more")}
        </button>
      )}
    </div>
  );
};

export default CollapsibleMarkdown;

import React, { useRef } from "react";
import Link from "core/components/Link";
import { getUrl, getObject } from "./mapper";
import useHighlightRow from "./useHighlightRow";
import { useRouter } from "next/router";

type HighlightedLinkProps = {
  item: any;
  highlightedIndex: number;
  isActive: boolean;
  data: Array<any>;
};

const HighlightedLink = ({
  item,
  highlightedIndex,
  isActive,
  data,
}: HighlightedLinkProps) => {
  const router = useRouter();
  const { workspaceSlug: currentWorkspaceSlug } = router.query as {
    workspaceSlug: string | undefined;
  };

  const resultRefs = useRef<(HTMLDivElement | null)[]>([]);
  useHighlightRow(resultRefs, highlightedIndex, [isActive, data]);

  const index = data.indexOf(item);
  const name = getObject(item).name;
  return (
    <div
      ref={(el) => {
        resultRefs.current[index] = el;
      }}
      tabIndex={-1}
      className="focus:outline-none"
    >
      <Link href={getUrl(item, currentWorkspaceSlug)}>
        <div title={name} className="truncate">
          {name}
        </div>
      </Link>
    </div>
  );
};

export default HighlightedLink;

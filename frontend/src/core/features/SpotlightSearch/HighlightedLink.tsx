import React, { useRef } from "react";
import Link from "core/components/Link";
import { getLink, getObject } from "./mapper";
import useHighlightRow from "./useHighlightRow";
import { useRouter } from "next/router";
import clsx from "clsx";

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

  return (
    <div
      ref={(el) => {
        resultRefs.current[index] = el;
      }}
      tabIndex={-1}
      className={clsx(
        "focus:outline-none hover:w-auto hover:fixed",
        index === highlightedIndex ? "hover:bg-blue-100" : "hover:bg-white",
      )}
    >
      <Link href={{ pathname: getLink(item, currentWorkspaceSlug) }}>
        <div className="truncate">{getObject(item).name}</div>
      </Link>
    </div>
  );
};

export default HighlightedLink;

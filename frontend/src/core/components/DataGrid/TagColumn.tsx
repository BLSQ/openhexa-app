import CountryBadge from "core/features/CountryBadge";
import Tag from "core/features/Tag";
import { ReactElement, useMemo } from "react";
import { BaseColumnProps } from "./BaseColumn";
import { useCellContext } from "./helpers";

type TagColumnProps = {
  max?: number;
  defaultValue?: ReactElement | string;
} & BaseColumnProps;

const TagColumn = (props: TagColumnProps) => {
  const { max, defaultValue } = props;
  const cell = useCellContext();
  const tags = useMemo(() => {
    if (!cell.value) return [];

    return Array.isArray(cell.value) ? cell.value : [cell.value];
  }, [cell.value]);

  const displayedTags = useMemo(
    () => (max ? tags.slice(0, max) : tags),
    [max, tags],
  );

  return (
    <div className="flex flex-wrap items-center gap-2">
      {!tags?.length && defaultValue}
      {displayedTags.map((tag) => (
        <Tag key={tag.id} tag={tag} />
      ))}
      {tags.length !== displayedTags.length && (
        <span>(+ {tags.length - displayedTags.length})</span>
      )}
    </div>
  );
};

export default TagColumn;

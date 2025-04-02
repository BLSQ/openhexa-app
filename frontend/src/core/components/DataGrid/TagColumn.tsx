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
  const allTags = useMemo(() => {
    if (!cell.value) return [];

    return Array.isArray(cell.value) ? cell.value : [cell.value];
  }, [cell.value]);

  const tags = useMemo(
    () => (max ? allTags.slice(0, max) : allTags),
    [max, allTags],
  );

  return (
    <div className="flex flex-wrap items-center gap-2">
      {!allTags?.length && defaultValue}
      {tags.map((tag) => (
        <Tag key={tag.id} tag={tag} />
      ))}
      {allTags.length !== tags.length && (
        <span>(+ {allTags.length - tags.length})</span>
      )}
    </div>
  );
};

export default TagColumn;

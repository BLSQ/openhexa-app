import Tag from "core/features/Tag";
import { formatPipelineFunctionalType } from "workspaces/helpers/pipelines";
import { PipelineFunctionalType } from "graphql/types";

type TagType = {
  id: string;
  name: string;
};

type PipelineMetadataGridProps = {
  functionalType?: PipelineFunctionalType | null;
  tags?: TagType[];
  maxTags?: number;
  emptyText?: string;
  className?: string;
};

export const FunctionalTypeCell = ({
  functionalType,
  emptyText = "-",
  className = "",
}: {
  functionalType?: PipelineFunctionalType | null;
  emptyText?: string;
  className?: string;
}) => {
  return (
    <span className={`text-gray-600 text-sm ${className}`}>
      {functionalType ? formatPipelineFunctionalType(functionalType) : emptyText}
    </span>
  );
};

export const TagsCell = ({
  tags,
  maxTags,
  emptyText = "-",
  className = "",
}: {
  tags?: TagType[];
  maxTags?: number;
  emptyText?: string;
  className?: string;
}) => {
  if (!tags || tags.length === 0) {
    return <span className={`text-gray-400 text-xs ${className}`}>{emptyText}</span>;
  }

  const displayTags = maxTags ? tags.slice(0, maxTags) : tags;
  const remainingCount = maxTags && tags.length > maxTags ? tags.length - maxTags : 0;

  return (
    <div className={`flex flex-wrap gap-1 ${className}`}>
      {displayTags.map((tag) => (
        <Tag key={tag.id} tag={tag} className="text-xs" />
      ))}
      {remainingCount > 0 && (
        <span className="text-xs text-gray-500">+{remainingCount}</span>
      )}
    </div>
  );
};

const PipelineMetadataGrid = ({
  functionalType,
  tags,
  maxTags,
  emptyText = "-",
  className = "",
}: PipelineMetadataGridProps) => {
  if (functionalType !== undefined) {
    return <FunctionalTypeCell functionalType={functionalType} emptyText={emptyText} className={className} />;
  }

  if (tags !== undefined) {
    return <TagsCell tags={tags} maxTags={maxTags} emptyText={emptyText} className={className} />;
  }

  return null;
};

export default PipelineMetadataGrid;

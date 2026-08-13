import clsx from "clsx";
import { SavedQueryVisibility } from "graphql/types";
import { useSavedQueryVisibilityOption } from "workspaces/features/SavedQueries/savedQueryVisibility";

type SavedQueryVisibilityBadgeProps = {
  visibility: SavedQueryVisibility;
  className?: string;
};

// Read-only rendering of a query's sharing, used wherever visibility is shown
// but not editable (the list column, the toolbar without the rights to unshare).
const SavedQueryVisibilityBadge = ({
  visibility,
  className,
}: SavedQueryVisibilityBadgeProps) => {
  const { label, Icon } = useSavedQueryVisibilityOption(visibility);

  return (
    <span className={clsx("inline-flex items-center gap-1.5", className)}>
      <Icon className="h-4 w-4 shrink-0 text-gray-400" />
      {label}
    </span>
  );
};

export default SavedQueryVisibilityBadge;

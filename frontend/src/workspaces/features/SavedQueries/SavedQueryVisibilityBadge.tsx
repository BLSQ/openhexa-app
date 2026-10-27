import clsx from "clsx";
import Badge from "core/components/Badge";
import { SavedQueryVisibility } from "graphql/types";
import { useSavedQueryVisibilityOption } from "workspaces/features/SavedQueries/savedQueryVisibility";

type SavedQueryVisibilityBadgeProps = {
  visibility: SavedQueryVisibility;
  size?: "xs" | "sm" | "md";
  className?: string;
};

// Read-only rendering of a query's sharing, used wherever visibility is shown
// but not editable (the list column, the toolbar without the rights to change
// it, the public page). Same shape as the dataset visibility badge, so the
// datasets and saved queries lists read alike.
const SavedQueryVisibilityBadge = ({
  visibility,
  size = "xs",
  className,
}: SavedQueryVisibilityBadgeProps) => {
  const { label, Icon, badgeClassName } =
    useSavedQueryVisibilityOption(visibility);

  return (
    <Badge size={size} className={clsx("gap-1", badgeClassName, className)}>
      <Icon className="h-3.5 w-3.5 shrink-0" />
      {label}
    </Badge>
  );
};

export default SavedQueryVisibilityBadge;

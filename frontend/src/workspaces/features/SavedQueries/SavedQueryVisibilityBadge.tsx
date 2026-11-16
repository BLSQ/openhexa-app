import { BadgeProps } from "core/components/Badge";
import SharingBadge from "core/features/Sharing/SharingBadge";
import { SavedQueryVisibility } from "graphql/types";
import { useSavedQueryVisibilityOption } from "workspaces/features/SavedQueries/savedQueryVisibility";

type SavedQueryVisibilityBadgeProps = {
  visibility: SavedQueryVisibility;
  size?: BadgeProps["size"];
  className?: string;
};

const SavedQueryVisibilityBadge = ({
  visibility,
  ...props
}: SavedQueryVisibilityBadgeProps) => (
  <SharingBadge option={useSavedQueryVisibilityOption(visibility)} {...props} />
);

export default SavedQueryVisibilityBadge;

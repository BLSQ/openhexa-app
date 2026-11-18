import { BadgeProps } from "core/components/Badge";
import SharingBadge from "core/features/Sharing/SharingBadge";
import { useDatasetSharingOption } from "datasets/features/DatasetSharing/datasetSharing";
import { DatasetVisibility } from "graphql/types";

type DatasetVisibilityBadgeProps = {
  visibility: DatasetVisibility;
  size?: BadgeProps["size"];
  className?: string;
};

const DatasetVisibilityBadge = ({
  visibility,
  ...props
}: DatasetVisibilityBadgeProps) => (
  <SharingBadge option={useDatasetSharingOption(visibility)} {...props} />
);

export default DatasetVisibilityBadge;

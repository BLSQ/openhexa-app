import clsx from "clsx";
import Badge from "core/components/Badge";
import { DatasetVisibility } from "graphql/types";
import { useDatasetVisibilityOption } from "./datasetVisibility";

type DatasetVisibilityBadgeProps = {
  visibility: DatasetVisibility;
  size?: "xs" | "sm" | "md";
  className?: string;
};

const DatasetVisibilityBadge = ({
  visibility,
  size = "xs",
  className,
}: DatasetVisibilityBadgeProps) => {
  const { label, Icon, badgeClassName } =
    useDatasetVisibilityOption(visibility);

  return (
    <Badge size={size} className={clsx("gap-1", badgeClassName, className)}>
      <Icon className="h-3.5 w-3.5 shrink-0" />
      {label}
    </Badge>
  );
};

export default DatasetVisibilityBadge;

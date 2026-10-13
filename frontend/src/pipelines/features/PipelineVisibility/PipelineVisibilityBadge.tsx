import clsx from "clsx";
import Badge from "core/components/Badge";
import { PipelineVisibility } from "graphql/types";
import { usePipelineVisibilityOption } from "./pipelineVisibility";

type PipelineVisibilityBadgeProps = {
  visibility: PipelineVisibility;
  size?: "xs" | "sm" | "md";
  className?: string;
};

const PipelineVisibilityBadge = ({
  visibility,
  size = "xs",
  className,
}: PipelineVisibilityBadgeProps) => {
  const { label, Icon, badgeClassName } =
    usePipelineVisibilityOption(visibility);

  return (
    <Badge size={size} className={clsx("gap-1", badgeClassName, className)}>
      <Icon className="h-3.5 w-3.5 shrink-0" />
      {label}
    </Badge>
  );
};

export default PipelineVisibilityBadge;

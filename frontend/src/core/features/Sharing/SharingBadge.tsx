import clsx from "clsx";
import Badge, { BadgeProps } from "core/components/Badge";
import { SharingStyle } from "core/features/Sharing/sharingStyles";

type SharingBadgeProps = {
  option: SharingStyle & { label: string };
  size?: BadgeProps["size"];
  className?: string;
};

// Read-only rendering of who a resource is shared with.
const SharingBadge = ({ option, size, className }: SharingBadgeProps) => {
  const { label, Icon, badgeClassName } = option;
  return (
    <Badge size={size} className={clsx("gap-1", badgeClassName, className)}>
      <Icon className="h-3.5 w-3.5 shrink-0" />
      {label}
    </Badge>
  );
};

export default SharingBadge;

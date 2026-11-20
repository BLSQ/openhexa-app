import { GlobeAltIcon, LockClosedIcon } from "@heroicons/react/24/outline";
import clsx from "clsx";
import Badge, { BadgeProps } from "core/components/Badge";
import { useTranslation } from "next-i18next";

type WebappVisibilityBadgeProps = {
  isPublic: boolean;
  size?: BadgeProps["size"];
  className?: string;
};

// Same colours as the saved query visibility badge, so the lists read alike.
const WebappVisibilityBadge = ({
  isPublic,
  size,
  className,
}: WebappVisibilityBadgeProps) => {
  const { t } = useTranslation();
  const Icon = isPublic ? GlobeAltIcon : LockClosedIcon;

  return (
    <Badge
      size={size}
      className={clsx(
        "gap-1",
        isPublic
          ? "bg-blue-100 text-blue-800 ring-blue-600/20"
          : "bg-gray-100 text-gray-800 ring-gray-500/20",
        className,
      )}
    >
      <Icon className="h-3.5 w-3.5 shrink-0" />
      {isPublic ? t("Public") : t("Private")}
    </Badge>
  );
};

export default WebappVisibilityBadge;

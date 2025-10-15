import { useTranslation } from "next-i18next";
import Badge from "core/components/Badge";
import { CheckBadgeIcon } from "@heroicons/react/24/solid";
import clsx from "clsx";

interface TemplateBadgeProps {
  isOfficial: boolean;
  iconUrl?: string | null;
  size?: "sm" | "md";
  showIcon?: boolean;
}

const TemplateBadge = ({
  isOfficial,
  iconUrl,
  size = "md",
  showIcon = true
}: TemplateBadgeProps) => {
  const { t } = useTranslation();

  if (isOfficial) {
    return (
      <div className="flex items-center gap-1.5">
        {iconUrl && showIcon && (
          <img
            src={iconUrl}
            alt="Official template icon"
            className={clsx(
              "object-contain",
              size === "sm" ? "h-4 w-4" : "h-5 w-5"
            )}
          />
        )}
        <Badge className="bg-blue-50 text-blue-700 ring-blue-600/20 flex items-center gap-1">
          <CheckBadgeIcon className={clsx(size === "sm" ? "h-3 w-3" : "h-4 w-4")} />
          <span className={clsx(size === "sm" ? "text-xs" : "text-sm")}>
            {t("Official")}
          </span>
        </Badge>
      </div>
    );
  }

  return (
    <Badge className="bg-gray-50 text-gray-600 ring-gray-500/20">
      <span className={clsx(size === "sm" ? "text-xs" : "text-sm")}>
        {t("Community")}
      </span>
    </Badge>
  );
};

export default TemplateBadge;

import { useTranslation } from "next-i18next";
import Badge from "core/components/Badge";
import clsx from "clsx";

const PUBLISHER_BLUESQUARE = "Bluesquare";
const PUBLISHER_COMMUNITY = "Community";

interface TemplateBadgeProps {
  publisher?: string | null;
  size?: "sm" | "md";
  showIcon?: boolean;
}

const TemplateBadge = ({
  publisher,
  size = "md",
  showIcon = true,
}: TemplateBadgeProps) => {
  const { t } = useTranslation();

  if (publisher === PUBLISHER_BLUESQUARE) {
    return (
      <Badge className="bg-blue-50 text-blue-700 ring-blue-600/20 flex items-center gap-1.5">
        {showIcon && (
          <img
            src="/images/bluesquare-icon.svg"
            alt="Bluesquare"
            className={clsx(
              "object-contain",
              size === "sm" ? "h-3.5 w-3.5" : "h-4 w-4",
            )}
          />
        )}
        <span className={clsx(size === "sm" ? "text-xs" : "text-sm")}>
          Bluesquare
        </span>
      </Badge>
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

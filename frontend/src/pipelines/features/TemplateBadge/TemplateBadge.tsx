import { useTranslation } from "next-i18next";
import Badge from "core/components/Badge";
import clsx from "clsx";

interface PublisherStyle {
  label: string;
  icon?: string;
  colorClass: string;
  textClass: string;
  ringClass: string;
}

const PUBLISHER_STYLES: Record<string, PublisherStyle> = {
  Bluesquare: {
    label: "Bluesquare",
    icon: "/images/bluesquare-icon.svg",
    colorClass: "bg-blue-50",
    textClass: "text-blue-700",
    ringClass: "ring-blue-600/20",
  },
  Community: {
    label: "Community",
    colorClass: "bg-gray-50",
    textClass: "text-gray-600",
    ringClass: "ring-gray-500/20",
  },
};

interface TemplateBadgeProps {
  publisher?: string | null;
  size?: "sm" | "md";
  showIcon?: boolean;
}

const TemplateBadge = ({
  publisher = "Community",
  size = "md",
  showIcon = true,
}: TemplateBadgeProps) => {
  const { t } = useTranslation();
  const style = PUBLISHER_STYLES[publisher ?? "Community"] || PUBLISHER_STYLES.Community;

  return (
    <Badge
      className={clsx(
        "flex items-center gap-1.5",
        style.colorClass,
        style.textClass,
        style.ringClass,
      )}
    >
      {showIcon && style.icon && (
        <img
          src={style.icon}
          alt={style.label}
          className={clsx(
            "object-contain",
            size === "sm" ? "h-3.5 w-3.5" : "h-4 w-4",
          )}
        />
      )}
      <span className={clsx(size === "sm" ? "text-xs" : "text-sm")}>
        {style.label === "Bluesquare" ? "Bluesquare" : t("Community")}
      </span>
    </Badge>
  );
};

export default TemplateBadge;

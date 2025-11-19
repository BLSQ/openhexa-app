import { useTranslation } from "next-i18next";
import Badge from "core/components/Badge";
import clsx from "clsx";

interface Organization {
  name: string;
  logo?: string | null;
}

interface PublisherStyle {
  label: string;
  icon?: string;
  colorClass: string;
  textClass: string;
  ringClass: string;
}

const COMMUNITY_STYLE: PublisherStyle = {
  label: "Community",
  colorClass: "bg-gray-50",
  textClass: "text-gray-600",
  ringClass: "ring-gray-500/20",
};

const ORGANIZATION_STYLE: PublisherStyle = {
  label: "",
  colorClass: "bg-blue-50",
  textClass: "text-blue-700",
  ringClass: "ring-blue-600/20",
};

interface TemplateBadgeProps {
  organization?: Organization | null;
  validatedAt?: string | null;
  size?: "sm" | "md";
  showIcon?: boolean;
}

const TemplateBadge = ({
  organization,
  validatedAt,
  size = "md",
  showIcon = true,
}: TemplateBadgeProps) => {
  const { t } = useTranslation();

  const isValidated = validatedAt !== null && validatedAt !== undefined;
  const style = isValidated && organization
    ? { ...ORGANIZATION_STYLE, label: organization.name, icon: organization.logo || undefined }
    : COMMUNITY_STYLE;

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
        {isValidated && organization ? organization.name : t("Community")}
      </span>
    </Badge>
  );
};

export default TemplateBadge;

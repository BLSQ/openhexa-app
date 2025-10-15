import { useTranslation } from "next-i18next";
import Badge from "core/components/Badge";
import clsx from "clsx";

interface TemplatePublisherBadgeProps {
  organizationName?: string | null;
  organizationLogoUrl?: string | null;
  size?: "sm" | "md";
}

const TemplatePublisherBadge = ({
  organizationName,
  organizationLogoUrl,
  size = "md",
}: TemplatePublisherBadgeProps) => {
  const { t } = useTranslation();

  if (!organizationName) {
    return (
      <Badge className="bg-gray-50 text-gray-600 ring-gray-500/20">
        <span className={clsx(size === "sm" ? "text-xs" : "text-sm")}>
          {t("Community")}
        </span>
      </Badge>
    );
  }

  if (organizationLogoUrl) {
    return (
      <div
        className={clsx(
          "inline-flex items-center",
          size === "sm" ? "h-5" : "h-6"
        )}
        dangerouslySetInnerHTML={{ __html: organizationLogoUrl }}
      />
    );
  }

  return (
    <Badge className="bg-purple-50 text-purple-700 ring-purple-600/20">
      <span className={clsx(size === "sm" ? "text-xs" : "text-sm")}>
        {organizationName}
      </span>
    </Badge>
  );
};

export default TemplatePublisherBadge;

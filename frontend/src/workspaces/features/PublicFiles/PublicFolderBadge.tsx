import { GlobeAltIcon } from "@heroicons/react/24/outline";
import clsx from "clsx";
import Badge from "core/components/Badge";
import { useTranslation } from "next-i18next";

type PublicFolderBadgeProps = {
  className?: string;
};

// Same colours as the public badge of datasets, queries and pipelines, so the
// folder reads as the same kind of exposure.
const PublicFolderBadge = ({ className }: PublicFolderBadgeProps) => {
  const { t } = useTranslation();
  return (
    <Badge
      className={clsx(
        "gap-1 bg-blue-100 text-blue-800 ring-blue-600/20",
        className,
      )}
      title={t("Anyone with a link can read the files in this folder")}
    >
      <GlobeAltIcon className="h-3.5 w-3.5 shrink-0" />
      {t("Public")}
    </Badge>
  );
};

export default PublicFolderBadge;

import { useState } from "react";
import { useTranslation } from "next-i18next";
import Badge from "core/components/Badge";
import { OrganizationDataset_DatasetFragment } from "organizations/graphql/queries.generated";

type DatasetWorkspacesListProps = {
  dataset: OrganizationDataset_DatasetFragment;
  maxVisible?: number;
  size?: "xs" | "sm" | "md";
  emptyMessage?: string;
};

const DatasetWorkspacesList = ({
  dataset,
  maxVisible = 3,
  size = "xs",
  emptyMessage,
}: DatasetWorkspacesListProps) => {
  const { t } = useTranslation();
  const [isExpanded, setIsExpanded] = useState(false);

  if (dataset.sharedWithOrganization) {
    return (
      <Badge className="bg-green-100 text-green-800" size={size}>
        {t("Organization")}
      </Badge>
    );
  }

  const sharedWorkspaces = dataset.links.items.filter(
    (link) => link.workspace.slug !== dataset.workspace?.slug,
  );

  if (sharedWorkspaces.length === 0) {
    return (
      <span className="text-gray-500 text-sm italic">
        {emptyMessage || t("Source workspace only")}
      </span>
    );
  }

  const shouldShowToggle = sharedWorkspaces.length > maxVisible;
  const visibleWorkspaces = isExpanded
    ? sharedWorkspaces
    : sharedWorkspaces.slice(0, maxVisible);
  const remainingCount = sharedWorkspaces.length - maxVisible;

  return (
    <div className="flex flex-wrap gap-1">
      {visibleWorkspaces.map((link) => (
        <Badge key={link.workspace.slug} size={size}>
          {link.workspace.name}
        </Badge>
      ))}
      {shouldShowToggle && (
        <button
          onClick={() => setIsExpanded(!isExpanded)}
          className="text-sm text-blue-600 hover:text-blue-800 hover:underline cursor-pointer pl-1"
        >
          {isExpanded
            ? t("Show less")
            : t("+{{remainingCount}} more", { remainingCount })}
        </button>
      )}
    </div>
  );
};

export default DatasetWorkspacesList;

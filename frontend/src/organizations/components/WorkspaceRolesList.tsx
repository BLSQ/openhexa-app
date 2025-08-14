import { useState } from "react";
import { useTranslation } from "next-i18next";
import { gql } from "@apollo/client";
import WorkspaceRoleBadge from "workspaces/components/WorkspaceRoleBadge";
import { WorkspaceRoleFragment } from "./WorkspaceRolesList.generated";

type WorkspaceRolesListProps = {
  items: WorkspaceRoleFragment[];
  maxVisible?: number;
  size?: "xs" | "sm" | "md";
  emptyMessage?: string;
};

const WorkspaceRolesList = ({
  items,
  maxVisible = 3,
  size = "xs",
  emptyMessage,
}: WorkspaceRolesListProps) => {
  const { t } = useTranslation();
  const [isExpanded, setIsExpanded] = useState(false);

  if (items.length === 0) {
    return (
      <span className="text-gray-500 text-sm italic">
        {emptyMessage || t("No workspace access")}
      </span>
    );
  }

  const shouldShowToggle = items.length > maxVisible;
  const visibleItems = isExpanded ? items : items.slice(0, maxVisible);
  const remainingCount = items.length - maxVisible;

  return (
    <div className="flex flex-wrap gap-1">
      {visibleItems.map((item) => (
        <WorkspaceRoleBadge
          key={item.workspace.slug}
          role={item.role}
          workspaceName={item.workspace.name}
          size={size}
        />
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

WorkspaceRolesList.fragments = {
  workspaceMembership: gql`
    fragment WorkspaceRole on WorkspaceMembership {
      role
      workspace {
        name
        slug
      }
    }
  `,
};

export default WorkspaceRolesList;

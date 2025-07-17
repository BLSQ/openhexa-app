import { useState } from "react";
import { useTranslation } from "next-i18next";
import { gql } from "@apollo/client";
import WorkspaceRoleBadge from "workspaces/components/WorkspaceRoleBadge";
import { WorkspaceRoleFragment } from "./WorkspaceRolesList.generated";

type WorkspaceRolesListProps = {
  workspaceMemberships: WorkspaceRoleFragment[];
  maxVisible?: number;
  size?: "xs" | "sm" | "md";
};

const WorkspaceRolesList = ({
  workspaceMemberships,
  maxVisible = 3,
  size = "xs",
}: WorkspaceRolesListProps) => {
  const { t } = useTranslation();
  const [isExpanded, setIsExpanded] = useState(false);

  if (workspaceMemberships.length === 0) {
    return (
      <span className="text-gray-500 text-sm italic">
        {t("No workspace access")}
      </span>
    );
  }

  const shouldShowToggle = workspaceMemberships.length > maxVisible;
  const visibleMemberships = isExpanded
    ? workspaceMemberships
    : workspaceMemberships.slice(0, maxVisible);
  const remainingCount = workspaceMemberships.length - maxVisible;

  return (
    <div className="flex flex-wrap gap-1">
      {visibleMemberships.map((membership) => (
        <WorkspaceRoleBadge
          key={membership.workspace.slug}
          role={membership.role}
          workspaceName={membership.workspace.name}
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

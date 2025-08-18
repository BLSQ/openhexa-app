import { WorkspaceMembershipRole } from "graphql/types";
import Badge from "core/components/Badge";
import { formatWorkspaceMembershipRole } from "workspaces/helpers/workspace";
import clsx from "clsx";

type WorkspaceRoleBadgeProps = {
  role: WorkspaceMembershipRole;
  workspaceName?: string;
  size?: "xs" | "sm" | "md";
};

const WorkspaceRoleBadge = ({
  role,
  workspaceName,
  size = "xs",
}: WorkspaceRoleBadgeProps) => {
  const getRoleColors = (role: WorkspaceMembershipRole) => {
    switch (role) {
      case WorkspaceMembershipRole.Admin:
        return "bg-purple-50 text-purple-800 ring-purple-600/20";
      case WorkspaceMembershipRole.Editor:
        return "bg-green-50 text-green-800 ring-green-600/20";
      case WorkspaceMembershipRole.Viewer:
        return "bg-gray-50 text-gray-800 ring-gray-600/20";
      default:
        return "bg-gray-50 text-gray-800 ring-gray-600/20";
    }
  };

  const badgeContent = workspaceName
    ? `${workspaceName} · ${formatWorkspaceMembershipRole(role)}`
    : formatWorkspaceMembershipRole(role);

  return (
    <Badge size={size} className={clsx("text-xs", getRoleColors(role))}>
      {badgeContent}
    </Badge>
  );
};

export default WorkspaceRoleBadge;

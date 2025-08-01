import { OrganizationMembershipRole } from "graphql/types";
import Badge from "core/components/Badge";
import { formatOrganizationMembershipRole } from "organizations/helpers/organization";
import clsx from "clsx";

type OrganizationRoleBadgeProps = {
  role: OrganizationMembershipRole;
  size?: "xs" | "sm" | "md";
};

const OrganizationRoleBadge = ({
  role,
  size = "xs",
}: OrganizationRoleBadgeProps) => {
  const getRoleColors = (role: OrganizationMembershipRole) => {
    switch (role) {
      case OrganizationMembershipRole.Owner:
        return "bg-red-50 text-red-800 ring-red-600/20";
      case OrganizationMembershipRole.Admin:
        return "bg-orange-50 text-orange-800 ring-orange-600/20";
      case OrganizationMembershipRole.Member:
        return "bg-blue-50 text-blue-800 ring-blue-600/20";
      default:
        return "bg-gray-50 text-gray-800 ring-gray-600/20";
    }
  };

  return (
    <Badge size={size} className={clsx("text-xs", getRoleColors(role))}>
      {formatOrganizationMembershipRole(role)}
    </Badge>
  );
};

export default OrganizationRoleBadge;

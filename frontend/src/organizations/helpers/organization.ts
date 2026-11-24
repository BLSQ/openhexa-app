import { OrganizationMembershipRole } from "graphql/types";
import { i18n } from "next-i18next";

export function formatOrganizationMembershipRole(
  role: OrganizationMembershipRole,
) {
  switch (role) {
    case OrganizationMembershipRole.Owner:
      return i18n!.t("Owner");
    case OrganizationMembershipRole.Admin:
      return i18n!.t("Admin");
    case OrganizationMembershipRole.Member:
      return i18n!.t("Member");
    default:
      return i18n!.t("Unknown");
  }
}

/**
 * Turns a Console plan code (e.g. "openhexa_starter") into a display name ("Starter").
 */
export function formatPlanName(planCode: string) {
  return planCode
    .replace(/^openhexa_/, "")
    .split("_")
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(" ");
}

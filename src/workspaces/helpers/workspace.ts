import { WorkspaceMembershipRole } from "graphql/types";
import { i18n } from "next-i18next";
export function formatWorkspaceMembershipRole(role: WorkspaceMembershipRole) {
  switch (role) {
    case WorkspaceMembershipRole.Admin:
      return i18n!.t("Admin");
    case WorkspaceMembershipRole.Viewer:
      return i18n!.t("Viewer");
    case WorkspaceMembershipRole.Editor:
      return i18n!.t("Editor");
    default:
      return i18n!.t("Unknown");
  }
}

import { GlobeAltIcon, LockClosedIcon } from "@heroicons/react/24/outline";
import { SavedQueryVisibility } from "graphql/types";
import { useTranslation } from "next-i18next";
import { ComponentType, useMemo } from "react";

export type VisibilityOption = {
  value: SavedQueryVisibility;
  label: string;
  description: string;
  Icon: ComponentType<{ className?: string }>;
  iconClassName: string;
};

// Single source of truth for how visibility reads to users, so the save dialog,
// the editor toolbar and the list cannot drift apart. Ordered private-first, which
// is both the default for a new query and the order the design shows.
export const useSavedQueryVisibilityOptions = (): VisibilityOption[] => {
  const { t } = useTranslation();

  return useMemo(
    () => [
      {
        value: SavedQueryVisibility.Private,
        label: t("Private"),
        description: t("Only you can see this query."),
        Icon: LockClosedIcon,
        iconClassName: "text-gray-500",
      },
      {
        value: SavedQueryVisibility.Workspace,
        label: t("Workspace"),
        // Spells out that sharing also hands over write access: editors and admins
        // can change or delete a shared query, which "anyone can view and run it"
        // alone would let users read as read-only exposure.
        description: t(
          "Anyone in this workspace can view and run it. Editors and admins can also change or delete it.",
        ),
        Icon: GlobeAltIcon,
        iconClassName: "text-emerald-600",
      },
    ],
    [t],
  );
};

export const useSavedQueryVisibilityOption = (
  visibility: SavedQueryVisibility,
): VisibilityOption => {
  const options = useSavedQueryVisibilityOptions();
  // Falls back to private rather than crashing if the backend ever grows a value
  // this build does not know about: the safe reading of an unknown visibility.
  return options.find((option) => option.value === visibility) ?? options[0];
};

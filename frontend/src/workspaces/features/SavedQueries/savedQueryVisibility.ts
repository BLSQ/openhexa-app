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

// Binds each entry to its own key, so an option filed under the wrong visibility
// is a compile error rather than a picker whose radios submit the wrong value.
type VisibilityOptions = {
  [V in SavedQueryVisibility]: VisibilityOption & { value: V };
};

// The most exposed visibility this build knows of. A visibility added on the
// backend stops the record from compiling; that is the moment to reconsider this.
const MOST_EXPOSED = SavedQueryVisibility.Workspace;

// Single source of truth for how visibility reads to users, so the save dialog,
// the editor toolbar and the list cannot drift apart. Keyed by the enum on
// purpose: a visibility added on the backend then lands here as a compile error
// instead of silently rendering as one of the values this build happens to know.
// Declaration order is the order the design shows (`Object.values` preserves it).
const useVisibilityOptionsByValue = (): VisibilityOptions => {
  const { t } = useTranslation();

  return useMemo(
    () => ({
      [SavedQueryVisibility.Private]: {
        value: SavedQueryVisibility.Private,
        label: t("Private"),
        description: t("Only you can see this query."),
        Icon: LockClosedIcon,
        iconClassName: "text-gray-500",
      },
      [SavedQueryVisibility.Workspace]: {
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
    }),
    [t],
  );
};

export const useSavedQueryVisibilityOptions = (): VisibilityOption[] => {
  const byValue = useVisibilityOptionsByValue();
  return useMemo(() => Object.values(byValue), [byValue]);
};

export const useSavedQueryVisibilityOption = (
  visibility: SavedQueryVisibility,
): VisibilityOption => {
  const byValue = useVisibilityOptionsByValue();
  // Unreachable for any value this build was compiled against; only a bundle
  // still running while the backend already serves a newer visibility gets here.
  // Reading that as the most-exposed option we know, rather than the least, keeps
  // the badge from putting a padlock on a query nothing tells us is private. A
  // reload picks up the build that knows the real value.
  return byValue[visibility] ?? byValue[MOST_EXPOSED];
};

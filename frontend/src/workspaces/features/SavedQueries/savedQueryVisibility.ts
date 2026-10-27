import {
  GlobeAltIcon,
  LockClosedIcon,
  UserGroupIcon,
} from "@heroicons/react/24/outline";
import { SavedQueryVisibility } from "graphql/types";
import { useTranslation } from "next-i18next";
import { ComponentType, useMemo } from "react";

export type VisibilityOption = {
  value: SavedQueryVisibility;
  label: string;
  description: string;
  Icon: ComponentType<{ className?: string }>;
  iconClassName: string;
  // Colours of the read-only badge; the same scale the dataset badge uses, so
  // the two lists read alike.
  badgeClassName: string;
};

// Binds each entry to its own key, so an option filed under the wrong visibility
// is a compile error rather than a picker whose radios submit the wrong value.
type VisibilityOptions = {
  [V in SavedQueryVisibility]: VisibilityOption & { value: V };
};

// The most exposed visibility this build knows of. A visibility added on the
// backend stops the record from compiling; that is the moment to reconsider this.
const MOST_EXPOSED = SavedQueryVisibility.Public;

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
        badgeClassName: "bg-gray-100 text-gray-800 ring-gray-500/20",
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
        Icon: UserGroupIcon,
        iconClassName: "text-emerald-600",
        badgeClassName: "bg-green-100 text-green-800 ring-green-600/20",
      },
      [SavedQueryVisibility.Public]: {
        value: SavedQueryVisibility.Public,
        label: t("Public"),
        description: t(
          "Anyone with the link can run it and export its result, even without an OpenHEXA account. Members of the workspace keep the same access as for a shared query.",
        ),
        Icon: GlobeAltIcon,
        iconClassName: "text-blue-600",
        badgeClassName: "bg-blue-100 text-blue-800 ring-blue-600/20",
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

export type VisibilityRights = {
  // `permissions.updateVisibility`: the author's right to share and unshare.
  canShare: boolean;
  // `permissions.publish`: the author's, a workspace admin's or an organization
  // admin's right to make the query public and take it back to the workspace.
  canPublish: boolean;
};

// Mirrors SavedQuery._visibility_change_permission on the backend, so the
// controls never offer a switch the API would refuse.
export const canChangeVisibility = (
  from: SavedQueryVisibility,
  to: SavedQueryVisibility,
  { canShare, canPublish }: VisibilityRights,
) => {
  if (from === to) {
    return true;
  }
  const isPublishing =
    to === SavedQueryVisibility.Public ||
    (from === SavedQueryVisibility.Public &&
      to === SavedQueryVisibility.Workspace);
  return isPublishing ? canPublish : canShare;
};

// The permalink of a public query. Slugs are stable across renames and never
// reused, so the link outlives both.
export const getPublicSavedQueryPath = (slug: string) =>
  `/queries/${encodeURIComponent(slug)}`;

// The absolute form, for handing out. Only the browser knows the origin, so a
// server render gets the path alone; nothing renders the value, it is copied.
export const getPublicSavedQueryUrl = (slug: string) =>
  `${typeof window === "undefined" ? "" : window.location.origin}${getPublicSavedQueryPath(slug)}`;

import {
  SHARING_STYLES,
  SharingOption,
} from "core/features/Sharing/sharingStyles";
import { SavedQueryVisibility } from "graphql/types";
import { useTranslation } from "next-i18next";
import { useMemo } from "react";

export type VisibilityOption = SharingOption<SavedQueryVisibility>;

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
        ...SHARING_STYLES.private,
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
        ...SHARING_STYLES.workspace,
      },
      [SavedQueryVisibility.Public]: {
        value: SavedQueryVisibility.Public,
        label: t("Public"),
        description: t(
          "Anyone with the link can run it and export its result, even without an OpenHEXA account. Members of the workspace keep the same access as for a shared query.",
        ),
        ...SHARING_STYLES.public,
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
  canUpdateVisibility: boolean;
  // `permissions.share`: the author's, a workspace admin's or an organization
  // admin's right to make the query public and take it back to the workspace.
  canShare: boolean;
};

// Mirrors SavedQuery._visibility_change_permission on the backend, so the
// controls never offer a switch the API would refuse.
export const canChangeVisibility = (
  from: SavedQueryVisibility,
  to: SavedQueryVisibility,
  { canUpdateVisibility, canShare }: VisibilityRights,
) => {
  if (from === to) {
    return true;
  }
  const isSharingPublicly =
    to === SavedQueryVisibility.Public ||
    (from === SavedQueryVisibility.Public &&
      to === SavedQueryVisibility.Workspace);
  return isSharingPublicly ? canShare : canUpdateVisibility;
};

// The permalink of a public query. Slugs are stable across renames and never
// reused, so the link outlives both.
export const getPublicSavedQueryPath = (slug: string) =>
  `/queries/${encodeURIComponent(slug)}`;

// The absolute form, for handing out. Only the browser knows the origin, so a
// server render gets the path alone; nothing renders the value, it is copied.
export const getPublicSavedQueryUrl = (slug: string) =>
  `${typeof window === "undefined" ? "" : window.location.origin}${getPublicSavedQueryPath(slug)}`;

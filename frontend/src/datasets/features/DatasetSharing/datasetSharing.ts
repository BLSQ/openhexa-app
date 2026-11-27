import {
  SHARING_STYLES,
  SharingOption,
} from "core/features/Sharing/sharingStyles";
import { DatasetVisibility } from "graphql/types";
import { useTranslation } from "next-i18next";
import { useMemo } from "react";

// Keyed by the enum so a visibility added on the backend is a compile error here
// rather than a value silently rendered as another. Declaration order is the
// order shown to users.
const useOptionsByValue = (): {
  [V in DatasetVisibility]: SharingOption<V>;
} => {
  const { t } = useTranslation();
  return useMemo(
    () => ({
      [DatasetVisibility.Workspace]: {
        value: DatasetVisibility.Workspace,
        label: t("Private"),
        description: t(
          "Only the source workspace and the workspaces it is explicitly shared with can view and download it.",
        ),
        ...SHARING_STYLES.private,
      },
      [DatasetVisibility.Organization]: {
        value: DatasetVisibility.Organization,
        label: t("Organization"),
        description: t(
          "Every workspace of the organization can view and download it.",
        ),
        ...SHARING_STYLES.organization,
      },
      [DatasetVisibility.Public]: {
        value: DatasetVisibility.Public,
        label: t("Public"),
        description: t(
          "Anyone with the link can view and download it, even without an OpenHEXA account.",
        ),
        ...SHARING_STYLES.public,
      },
    }),
    [t],
  );
};

export const useDatasetSharingOptions =
  (): SharingOption<DatasetVisibility>[] => {
    const byValue = useOptionsByValue();
    return useMemo(() => Object.values(byValue), [byValue]);
  };

export const useDatasetSharingOption = (visibility: DatasetVisibility) =>
  useOptionsByValue()[visibility];

// The permalink of a public dataset. Its public slug never changes once set, so
// the link outlives renames.
export const getPublicDatasetPath = (publicSlug: string) =>
  `/datasets/${encodeURIComponent(publicSlug)}`;

// The absolute form, for handing out. Only the browser knows the origin, so a
// server render gets the path alone.
export const getPublicDatasetUrl = (publicSlug: string) =>
  `${typeof window === "undefined" ? "" : window.location.origin}${getPublicDatasetPath(publicSlug)}`;

// Mirrors Dataset.update_if_has_perm on the backend, so the picker never offers
// a switch the API would refuse.
export const canChangeDatasetVisibility = (
  from: DatasetVisibility,
  to: DatasetVisibility,
  { canUpdate, canShare }: { canUpdate: boolean; canShare: boolean },
) => {
  if (from === to) {
    return true;
  }
  const togglesPublic = [from, to].includes(DatasetVisibility.Public);
  return canUpdate && (!togglesPublic || canShare);
};

// Mirror validate_public_slug (backend/hexa/core/validators.py) so the slug is
// checked while typing. The backend stays the authority, and keeps checking
// whether the slug is already taken.
const PUBLIC_SLUG_RE = /^[a-z0-9]+(?:[-_][a-z0-9]+)*$/;
const PUBLIC_SLUG_MAX_LENGTH = 255;
const RESERVED_PUBLIC_SLUGS = new Set([
  "new",
  "search",
  "create",
  "edit",
  "settings",
  "api",
  "admin",
  "static",
  "assets",
  "media",
  "public",
  "explore",
  "embed",
  "download",
  "export",
]);

// Applied as the user types: fixes what has a single obvious fix (case, accents,
// spaces and dots), and leaves anything else for validation to point out.
export const normalizePublicSlug = (value: string) =>
  value
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .toLowerCase()
    .replace(/[\s.]/g, "-");

export const getPublicSlugError = (
  slug: string,
): "INVALID_FORMAT" | "RESERVED" | null => {
  if (slug.length > PUBLIC_SLUG_MAX_LENGTH || !PUBLIC_SLUG_RE.test(slug)) {
    return "INVALID_FORMAT";
  }
  return RESERVED_PUBLIC_SLUGS.has(slug) ? "RESERVED" : null;
};

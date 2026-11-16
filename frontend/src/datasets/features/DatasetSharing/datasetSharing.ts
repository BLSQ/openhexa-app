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

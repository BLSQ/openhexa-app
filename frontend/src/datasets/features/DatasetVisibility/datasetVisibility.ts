import {
  BuildingOffice2Icon,
  GlobeAltIcon,
  LockClosedIcon,
} from "@heroicons/react/24/outline";
import { DatasetVisibility } from "graphql/types";
import { useTranslation } from "next-i18next";
import { ComponentType, useMemo } from "react";

export type DatasetVisibilityOption = {
  value: DatasetVisibility;
  label: string;
  description: string;
  Icon: ComponentType<{ className?: string }>;
  iconClassName: string;
  badgeClassName: string;
};

// Keyed by the enum so that a visibility added on the backend is a compile
// error here rather than a picker that silently cannot select it.
type DatasetVisibilityOptions = {
  [V in DatasetVisibility]: DatasetVisibilityOption & { value: V };
};

// What an unknown value falls back to: the most exposed option, so a stale
// bundle never shows a padlock on a dataset the backend considers wider open.
const MOST_EXPOSED = DatasetVisibility.Public;

// Declaration order is the order the picker shows (`Object.values` preserves it).
const useDatasetVisibilityOptionsByValue = (): DatasetVisibilityOptions => {
  const { t } = useTranslation();

  return useMemo(
    () => ({
      [DatasetVisibility.Private]: {
        value: DatasetVisibility.Private,
        label: t("Private"),
        description: t(
          "Only the source workspace and the workspaces it is explicitly shared with.",
        ),
        Icon: LockClosedIcon,
        iconClassName: "text-gray-500",
        badgeClassName: "bg-gray-100 text-gray-800 ring-gray-500/20",
      },
      [DatasetVisibility.Organization]: {
        value: DatasetVisibility.Organization,
        label: t("Organization"),
        description: t(
          "Every workspace of the organization can view and download it.",
        ),
        Icon: BuildingOffice2Icon,
        iconClassName: "text-emerald-600",
        badgeClassName: "bg-green-100 text-green-800 ring-green-600/20",
      },
      [DatasetVisibility.Public]: {
        value: DatasetVisibility.Public,
        label: t("Public"),
        description: t(
          "Anyone with the link can view and download it, even without an OpenHEXA account.",
        ),
        Icon: GlobeAltIcon,
        iconClassName: "text-blue-600",
        badgeClassName: "bg-blue-100 text-blue-800 ring-blue-600/20",
      },
    }),
    [t],
  );
};

export const useDatasetVisibilityOptions = (): DatasetVisibilityOption[] => {
  const byValue = useDatasetVisibilityOptionsByValue();
  return useMemo(() => Object.values(byValue), [byValue]);
};

export const useDatasetVisibilityOption = (
  visibility: DatasetVisibility,
): DatasetVisibilityOption => {
  const byValue = useDatasetVisibilityOptionsByValue();
  return byValue[visibility] ?? byValue[MOST_EXPOSED];
};

export const getPublicDatasetPath = (datasetId: string) =>
  `/datasets/${encodeURIComponent(datasetId)}`;

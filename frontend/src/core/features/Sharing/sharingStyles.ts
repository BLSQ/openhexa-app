import {
  BuildingOfficeIcon,
  GlobeAltIcon,
  LockClosedIcon,
  UserGroupIcon,
} from "@heroicons/react/24/outline";
import { ComponentType } from "react";

export type SharingStyle = {
  Icon: ComponentType<{ className?: string }>;
  iconClassName: string;
  badgeClassName: string;
};

export type SharingOption<V extends string> = SharingStyle & {
  value: V;
  label: string;
  description: string;
};

// One look per reach, shared by every shareable resource (saved queries, web
// apps, datasets...), so the same level of exposure reads the same everywhere.
export const SHARING_STYLES = {
  private: {
    Icon: LockClosedIcon,
    iconClassName: "text-gray-500",
    badgeClassName: "bg-gray-100 text-gray-800 ring-gray-500/20",
  },
  workspace: {
    Icon: UserGroupIcon,
    iconClassName: "text-emerald-600",
    badgeClassName: "bg-green-100 text-green-800 ring-green-600/20",
  },
  // Same colours as workspace: both read as "shared internally".
  organization: {
    Icon: BuildingOfficeIcon,
    iconClassName: "text-emerald-600",
    badgeClassName: "bg-green-100 text-green-800 ring-green-600/20",
  },
  public: {
    Icon: GlobeAltIcon,
    iconClassName: "text-blue-600",
    badgeClassName: "bg-blue-100 text-blue-800 ring-blue-600/20",
  },
} satisfies Record<string, SharingStyle>;

import { GlobeAltIcon, UserGroupIcon } from "@heroicons/react/24/outline";
import { PipelineVisibility } from "graphql/types";
import { useTranslation } from "next-i18next";
import { ComponentType, useMemo } from "react";

export type VisibilityOption = {
  value: PipelineVisibility;
  label: string;
  description: string;
  Icon: ComponentType<{ className?: string }>;
  iconClassName: string;
  // Colours of the read-only badge; the same scale the dataset and saved query
  // badges use, so the three read alike.
  badgeClassName: string;
};

// Binds each entry to its own key, so an option filed under the wrong visibility
// is a compile error rather than a picker whose radios submit the wrong value.
type VisibilityOptions = {
  [V in PipelineVisibility]: VisibilityOption & { value: V };
};

const MOST_EXPOSED = PipelineVisibility.Public;

// Single source of truth for how visibility reads to users. Keyed by the enum
// on purpose: a visibility added on the backend lands here as a compile error
// instead of silently rendering as one of the values this build happens to know.
const useVisibilityOptionsByValue = (): VisibilityOptions => {
  const { t } = useTranslation();

  return useMemo(
    () => ({
      [PipelineVisibility.Workspace]: {
        value: PipelineVisibility.Workspace,
        label: t("Workspace"),
        description: t("Only members of this workspace can see and run it."),
        Icon: UserGroupIcon,
        iconClassName: "text-emerald-600",
        badgeClassName: "bg-green-100 text-green-800 ring-green-600/20",
      },
      [PipelineVisibility.Public]: {
        value: PipelineVisibility.Public,
        label: t("Public"),
        description: t(
          "Anyone with the link can run it and follow their run, even without an OpenHEXA account. They only fill in the plain parameters; the others use their default value.",
        ),
        Icon: GlobeAltIcon,
        iconClassName: "text-blue-600",
        badgeClassName: "bg-blue-100 text-blue-800 ring-blue-600/20",
      },
    }),
    [t],
  );
};

export const usePipelineVisibilityOptions = (): VisibilityOption[] => {
  const byValue = useVisibilityOptionsByValue();
  return useMemo(() => Object.values(byValue), [byValue]);
};

export const usePipelineVisibilityOption = (
  visibility: PipelineVisibility,
): VisibilityOption => {
  const byValue = useVisibilityOptionsByValue();
  // Only a bundle still running while the backend already serves a newer
  // visibility gets past the lookup; reading that as the most-exposed option
  // keeps the badge from understating what the pipeline is.
  return byValue[visibility] ?? byValue[MOST_EXPOSED];
};

// The permalink of a public pipeline. Codes are only unique within a workspace,
// so the id is what identifies it from outside.
export const getPublicPipelinePath = (pipelineId: string) =>
  `/run/${encodeURIComponent(pipelineId)}`;

export const getPublicPipelineRunPath = (pipelineId: string, runId: string) =>
  `${getPublicPipelinePath(pipelineId)}/${encodeURIComponent(runId)}`;

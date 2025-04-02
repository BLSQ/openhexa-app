import { PipelineRunStatus } from "graphql/types";
import { i18n } from "next-i18next";

export function formatPipelineRunStatus(
  status: PipelineRunStatus | PipelineRunStatus,
) {
  switch (status) {
    case PipelineRunStatus.Failed:
      return i18n!.t("Failed");
    case PipelineRunStatus.Queued:
      return i18n!.t("Queued");
    case PipelineRunStatus.Running:
      return i18n!.t("Running");
    case PipelineRunStatus.Success:
      return i18n!.t("Succeeded");
    case PipelineRunStatus.Stopped:
      return i18n!.t("Stopped");
    case PipelineRunStatus.Terminating:
      return i18n!.t("Terminating");
  }
}

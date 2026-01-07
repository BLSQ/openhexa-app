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
    case PipelineRunStatus.Skipped:
      return i18n!.t("Skipped");
  }
}

export function getPipelineRunStatusBadgeClassName(status: PipelineRunStatus) {
  switch (status) {
    case PipelineRunStatus.Stopped:
      return "bg-yellow-100 text-gray-600";
    case PipelineRunStatus.Failed:
      return "bg-red-100 text-red-500";
    case PipelineRunStatus.Queued:
      return "bg-gray-100 text-gray-600";
    case PipelineRunStatus.Running:
    case PipelineRunStatus.Terminating:
      return "bg-sky-100 text-sky-600";
    case PipelineRunStatus.Success:
      return "bg-emerald-50 text-emerald-500";
    case PipelineRunStatus.Skipped:
      return "bg-gray-100 text-gray-500";
  }
}

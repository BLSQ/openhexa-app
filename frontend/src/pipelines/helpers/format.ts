import { ParameterType, PipelineParameter, PipelineRunStatus } from "graphql/types";
import isNil from "lodash/isNil";
import { i18n } from "next-i18next";
import { isConnectionParameter } from "workspaces/helpers/pipelines";

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

export function formatParamValue(
  entry: PipelineParameter & { value: unknown },
): string {
  if (entry.type === ParameterType.Bool) {
    return entry.value ? "✓" : "✗";
  }
  if (entry.type === ParameterType.Secret) {
    return entry.value ? "••••••" : "-";
  }
  if (isNil(entry.value)) {
    return "-";
  }
  if (entry.multiple && Array.isArray(entry.value)) {
    return entry.value.map(String).join(", ");
  }
  if (isConnectionParameter(entry.type)) {
    return String(entry.value);
  }
  return String(entry.value);
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

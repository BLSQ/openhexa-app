import { DagRunStatus, PipelineRunStatus } from "graphql-types";
import { i18n } from "next-i18next";

export function formatDAGRunStatus(status: DagRunStatus | PipelineRunStatus) {
  switch (status) {
    case DagRunStatus.Failed:
      return i18n!.t("Failed");
    case DagRunStatus.Queued:
      return i18n!.t("Queued");
    case DagRunStatus.Running:
      return i18n!.t("Running");
    case DagRunStatus.Success:
      return i18n!.t("Succeeded");
  }
}

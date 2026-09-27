import { StopIcon } from "@heroicons/react/24/solid";
import Button from "core/components/Button";
import Clipboard from "core/components/Clipboard";
import { DetailBadge, SettingsCard } from "core/components/DetailShell";
import Link from "core/components/Link";
import Spinner from "core/components/Spinner";
import Switch from "core/components/Switch";
import Time from "core/components/Time";
import TruncatedText from "core/components/TruncatedText";
import User from "core/features/User";
import { formatDuration } from "core/helpers/time";
import {
  PipelineParameter,
  PipelineRunTrigger,
  PipelineType,
} from "graphql/types";
import isNil from "lodash/isNil";
import { DateTime } from "luxon";
import { useTranslation } from "next-i18next";
import PipelineRunStatusBadge from "pipelines/features/PipelineRunStatusBadge";
import RunLogs from "pipelines/features/RunLogs";
import RunMessages from "pipelines/features/RunMessages";
import { ReactNode, useMemo, useState } from "react";
import RunOutputsTable from "workspaces/features/RunOutputsTable";
import StopPipelineDialog from "workspaces/features/StopPipelineDialog";
import {
  formatPipelineSource,
  getPipelineRunConfig,
  isConnectionParameter,
} from "workspaces/helpers/pipelines";
import usePipelineRunDetail from "./usePipelineRunDetail";

const Field = ({ label, children }: { label: string; children: ReactNode }) => (
  <div className="min-w-0">
    <dt className="text-[11px] font-semibold uppercase tracking-wide text-gray-400">
      {label}
    </dt>
    <dd className="mt-1 text-[13px] text-gray-700">{children}</dd>
  </div>
);

type PipelineRunDetailProps = {
  workspaceSlug: string;
  runId: string;
};

const PipelineRunDetail = ({
  workspaceSlug,
  runId,
}: PipelineRunDetailProps) => {
  const { t } = useTranslation();
  const [isStopPipelineDialogOpen, setIsStopPipelineDialogOpen] =
    useState(false);
  const [areLogsVisible, setLogsVisible] = useState(false);

  const {
    data,
    run,
    isFinished,
    messageStream: {
      messages: sseMessages,
      isStreaming,
      streamError,
      reload: reloadStream,
    },
  } = usePipelineRunDetail(workspaceSlug, runId);

  const config = useMemo(() => (run ? getPipelineRunConfig(run) : []), [run]);

  if (!data?.workspace || !run) {
    return (
      <div className="flex items-center justify-center py-12">
        <Spinner size="sm" />
      </div>
    );
  }

  const { workspace } = data;
  const hasOutputs = run.datasetVersions.length + run.outputs.length > 0;

  const renderParameterValue = (entry: PipelineParameter & { value: any }) => {
    if (entry.type === "str" && entry.value) {
      const text = entry.multiple ? entry.value.join(", ") : entry.value;
      return (
        <TruncatedText lines={6} expandable>
          {text}
        </TruncatedText>
      );
    }
    if (entry.type === "bool") {
      return <Switch checked={entry.value} disabled />;
    }
    if (
      (entry.type === "int" || entry.type === "float") &&
      !isNil(entry.value)
    ) {
      const text = entry.multiple
        ? entry.value.join(", ")
        : String(entry.value);
      return (
        <TruncatedText lines={6} expandable>
          {text}
        </TruncatedText>
      );
    }
    if (isConnectionParameter(entry.type) && entry.value) {
      return (
        <TruncatedText lines={6} expandable>
          {entry.value}
        </TruncatedText>
      );
    }
    if (entry.type === "dataset") {
      return (
        <Link
          href={`/workspaces/${encodeURIComponent(
            workspaceSlug,
          )}/datasets/${encodeURIComponent(entry.value)}/from/${encodeURIComponent(workspaceSlug)}`}
        >
          {entry.value}
        </Link>
      );
    }
    if (entry.type === "file" && entry.value) {
      return (
        <TruncatedText lines={6} expandable>
          {entry.value}
        </TruncatedText>
      );
    }
    if (entry.type === "secret" && entry.value) {
      return "••••••";
    }

    return "-";
  };

  return (
    <div className="space-y-4">
      <SettingsCard>
        <div className="flex flex-wrap items-center gap-x-4 gap-y-3">
          <div className="min-w-0">
            <Time
              datetime={run.executionDate}
              className="truncate text-sm font-semibold text-gray-900"
            />
            <div className="mt-1 text-[13px] text-gray-500">
              {DateTime.fromISO(run.executionDate).toRelative()}
            </div>
          </div>
          <div className="ml-auto flex items-center gap-3">
            <div title={run.executionDate} suppressHydrationWarning>
              <PipelineRunStatusBadge run={run} />
            </div>
            {!isFinished && run.pipeline.permissions.stopPipeline && (
              <Button
                variant="danger"
                size="md"
                leadingIcon={<StopIcon className="h-4 w-4" />}
                onClick={() => setIsStopPipelineDialogOpen(true)}
              >
                {t("Stop")}
              </Button>
            )}
          </div>
        </div>
      </SettingsCard>

      <SettingsCard title={t("Details")}>
        <dl className="grid grid-cols-2 gap-x-8 gap-y-4 sm:grid-cols-3">
          <Field label={t("Trigger")}>
            {run.triggerMode === PipelineRunTrigger.Manual && t("Manual")}
            {run.triggerMode === PipelineRunTrigger.Scheduled && t("Scheduled")}
            {run.triggerMode === PipelineRunTrigger.Webhook && t("Webhook")}
          </Field>
          <Field label={t("User")}>
            {run.user ? <User user={run.user} /> : "-"}
          </Field>
          <Field label={t("Duration")}>
            {run.duration ? formatDuration(run.duration) : "-"}
          </Field>
          <Field label={t("Version")}>
            {run.version ? (
              <code className="font-mono text-gray-700">
                {run.version.versionName}
              </code>
            ) : (
              "-"
            )}
          </Field>
          <Field label={t("Timeout")}>
            {run.timeout ? formatDuration(run.timeout) : "-"}
          </Field>
          <Field label={t("Source")}>
            <DetailBadge color="gray">
              {formatPipelineSource(
                run.pipeline.type,
                !!run.pipeline.sourceTemplate,
              )}
            </DetailBadge>
          </Field>
          {run.pipeline.type === PipelineType.Notebook && (
            <Field label={t("Notebook")}>
              <code className="font-mono text-gray-700">
                {run.pipeline.notebookPath}
              </code>
            </Field>
          )}
          {run.stoppedBy && (
            <Field label={t("Stopped by")}>
              <User user={run.stoppedBy} />
            </Field>
          )}
        </dl>
      </SettingsCard>

      {run.pipeline.type === PipelineType.ZipFile && (
        <SettingsCard title={t("Parameters")}>
          {config.length > 0 ? (
            <dl className="grid grid-cols-1 gap-x-8 gap-y-4 sm:grid-cols-2">
              {config.map((entry) => (
                <Field key={entry.name} label={entry.name}>
                  {renderParameterValue(entry)}
                </Field>
              ))}
            </dl>
          ) : (
            <p className="text-sm italic text-gray-500">
              {t("This run has no parameters.")}
            </p>
          )}
        </SettingsCard>
      )}

      {isFinished && (
        <SettingsCard title={t("Outputs")}>
          {hasOutputs ? (
            <RunOutputsTable workspace={workspace} run={run} />
          ) : (
            <p className="text-sm italic text-gray-500">{t("No outputs")}</p>
          )}
        </SettingsCard>
      )}

      <SettingsCard title={t("Messages")}>
        {/* Keyed on the run so a run change recreates the message stream. */}
        <RunMessages
          key={run.id}
          run={run}
          messages={isFinished ? undefined : sseMessages}
          isStreaming={isStreaming}
          streamError={streamError}
          onReload={reloadStream}
        />
      </SettingsCard>

      <SettingsCard
        title={t("Logs")}
        actions={
          <div className="flex items-center gap-3">
            {run.logs && (
              <Clipboard value={run.logs} iconClassName="h-3.5 w-3.5" />
            )}
            <button
              onClick={() => setLogsVisible((visible) => !visible)}
              className="text-xs font-medium text-gray-500 hover:text-gray-700"
            >
              {areLogsVisible ? t("Hide") : t("Show")}
            </button>
          </div>
        }
      >
        {areLogsVisible && <RunLogs run={run} />}
      </SettingsCard>

      <StopPipelineDialog
        open={isStopPipelineDialogOpen}
        pipeline={run.pipeline}
        onClose={() => setIsStopPipelineDialogOpen(false)}
        run={run}
      />
    </div>
  );
};

export default PipelineRunDetail;

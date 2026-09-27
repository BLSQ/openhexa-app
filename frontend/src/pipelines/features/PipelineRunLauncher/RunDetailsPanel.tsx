import {
  ArrowPathIcon,
  ArrowUpRightIcon,
  ChevronDownIcon,
} from "@heroicons/react/24/outline";
import { StopIcon } from "@heroicons/react/24/solid";
import clsx from "clsx";
import Button from "core/components/Button";
import Clipboard from "core/components/Clipboard";
import Link from "core/components/Link";
import SidePanel from "core/components/SidePanel";
import Spinner from "core/components/Spinner";
import User from "core/features/User";
import useInterval from "core/hooks/useInterval";
import { PipelineRunTrigger } from "graphql/types";
import { useTranslation } from "next-i18next";
import usePipelineRunDetail from "pipelines/features/PipelineRunDetail/usePipelineRunDetail";
import PipelineRunStatusBadge from "pipelines/features/PipelineRunStatusBadge";
import RunLogs from "pipelines/features/RunLogs";
import RunMessages from "pipelines/features/RunMessages";
import { ReactNode, useState } from "react";
import RunOutputsTable from "workspaces/features/RunOutputsTable";
import StopPipelineDialog from "workspaces/features/StopPipelineDialog";
import {
  formatElapsed,
  formatStartedAt,
  getRunElapsedSeconds,
} from "./helpers";

const Field = ({ label, children }: { label: string; children: ReactNode }) => (
  <div className="min-w-0">
    <dt className="text-[11px] font-medium uppercase tracking-wide text-gray-400">
      {label}
    </dt>
    <dd className="mt-0.5 truncate text-[13px] text-gray-900">{children}</dd>
  </div>
);

const Section = ({
  title,
  actions,
  children,
  className,
}: {
  title: ReactNode;
  actions?: ReactNode;
  children?: ReactNode;
  className?: string;
}) => (
  <section
    className={clsx("border-b-2 border-gray-100 px-5 py-3.5", className)}
  >
    <div className="mb-2 flex items-center justify-between">
      <h4 className="text-[13px] font-semibold text-gray-900">{title}</h4>
      {actions}
    </div>
    {children}
  </section>
);

type RunDetailsPanelProps = {
  workspaceSlug: string;
  pipelineCode: string;
  pipelineName: string;
  runId: string;
  canRun: boolean;
  onClose: () => void;
  onRunAgain: () => Promise<unknown>;
};

const RunDetailsPanel = ({
  workspaceSlug,
  pipelineCode,
  pipelineName,
  runId,
  canRun,
  onClose,
  onRunAgain,
}: RunDetailsPanelProps) => {
  const { t } = useTranslation();
  const [isStopDialogOpen, setStopDialogOpen] = useState(false);
  const [areLogsVisible, setLogsVisible] = useState(false);
  const [isRelaunching, setRelaunching] = useState(false);
  const [relaunchError, setRelaunchError] = useState<string | null>(null);
  const [now, setNow] = useState(() => Date.now());

  const {
    data,
    run,
    isFinished,
    messageStream: { messages, isStreaming, streamError, reload },
  } = usePipelineRunDetail(workspaceSlug, runId);

  useInterval(() => setNow(Date.now()), isFinished ? null : 1000);

  const runPageHref = `/workspaces/${encodeURIComponent(
    workspaceSlug,
  )}/pipelines/${encodeURIComponent(pipelineCode)}/runs/${encodeURIComponent(
    runId,
  )}`;

  const handleRunAgain = async () => {
    setRelaunching(true);
    setRelaunchError(null);
    try {
      await onRunAgain();
    } catch (error) {
      setRelaunchError((error as Error).message);
    } finally {
      setRelaunching(false);
    }
  };

  const hasOutputs = run
    ? run.datasetVersions.length + run.outputs.length > 0
    : false;

  return (
    <SidePanel.Content
      title={
        <>
          {t("Run details")}
          {run && <PipelineRunStatusBadge run={run} />}
        </>
      }
      subtitle={`${pipelineName} · ${t("started {{time}}", {
        time: formatStartedAt(run?.executionDate),
      })}`}
      headerActions={
        <Link
          href={runPageHref}
          title={t("Open full run page")}
          customStyle="flex rounded-sm p-1.5 text-gray-500 hover:bg-gray-100 hover:text-gray-700"
        >
          <ArrowUpRightIcon className="h-4 w-4" />
        </Link>
      }
      onClose={onClose}
      footer={
        <>
          <Link
            href={runPageHref}
            customStyle="inline-flex items-center gap-1.5 text-[13px] font-medium text-blue-600 hover:text-blue-700"
          >
            {t("Open full run page")}
            <ArrowUpRightIcon className="h-3.5 w-3.5" />
          </Link>
          <div className="flex-1" />
          {relaunchError && (
            <span className="truncate text-xs text-red-600">
              {relaunchError}
            </span>
          )}
          {run && !isFinished && run.pipeline.permissions.stopPipeline && (
            <Button
              variant="danger"
              leadingIcon={<StopIcon className="h-4 w-4" />}
              onClick={() => setStopDialogOpen(true)}
            >
              {t("Stop")}
            </Button>
          )}
          {run && isFinished && canRun && (
            <Button
              variant="primary"
              disabled={isRelaunching}
              leadingIcon={
                isRelaunching ? (
                  <Spinner size="xs" />
                ) : (
                  <ArrowPathIcon className="h-4 w-4" />
                )
              }
              onClick={handleRunAgain}
            >
              {t("Run again")}
            </Button>
          )}
        </>
      }
    >
      {!run || !data?.workspace ? (
        <div className="flex items-center justify-center py-12">
          <Spinner size="sm" />
        </div>
      ) : (
        <div>
          <dl className="grid grid-cols-2 gap-x-4 gap-y-2.5 border-b-2 border-gray-100 px-5 py-3.5">
            <Field label={t("Version")}>
              {run.version?.versionName ?? "-"}
            </Field>
            <Field label={t("Trigger")}>
              {run.triggerMode === PipelineRunTrigger.Manual && t("Manual")}
              {run.triggerMode === PipelineRunTrigger.Scheduled &&
                t("Scheduled")}
              {run.triggerMode === PipelineRunTrigger.Webhook && t("Webhook")}
            </Field>
            <Field label={t("User")}>
              {run.user ? <User user={run.user} /> : "-"}
            </Field>
            <Field label={t("Duration")}>
              <span className="font-mono">
                {formatElapsed(getRunElapsedSeconds(run, isFinished, now))}
              </span>
            </Field>
          </dl>

          <Section title={t("Messages")}>
            <RunMessages
              key={run.id}
              run={run}
              messages={isFinished ? undefined : messages}
              isStreaming={isStreaming}
              streamError={streamError}
              onReload={reload}
            />
          </Section>

          {isFinished && (
            <Section title={t("Outputs")}>
              {hasOutputs ? (
                <RunOutputsTable workspace={data.workspace} run={run} />
              ) : (
                <p className="text-[13px] italic text-gray-600">
                  {t("No outputs")}
                </p>
              )}
            </Section>
          )}

          <Section
            className="border-b-0"
            title={
              <button
                type="button"
                onClick={() => setLogsVisible((visible) => !visible)}
                className="flex items-center gap-1.5"
              >
                {t("Logs")}
                <ChevronDownIcon
                  className={clsx(
                    "h-3.5 w-3.5 text-gray-500 transition-transform",
                    areLogsVisible && "rotate-180",
                  )}
                />
              </button>
            }
            actions={
              areLogsVisible &&
              run.logs && (
                <Clipboard value={run.logs} iconClassName="h-3.5 w-3.5" />
              )
            }
          >
            {areLogsVisible && <RunLogs run={run} />}
          </Section>

          <StopPipelineDialog
            open={isStopDialogOpen}
            pipeline={run.pipeline}
            onClose={() => setStopDialogOpen(false)}
            run={run}
          />
        </div>
      )}
    </SidePanel.Content>
  );
};

export default RunDetailsPanel;

import { ArrowPathIcon } from "@heroicons/react/24/outline";
import { StopIcon } from "@heroicons/react/24/solid";
import Badge from "core/components/Badge";
import Block from "core/components/Block";
import Breadcrumbs from "core/components/Breadcrumbs";
import Button from "core/components/Button";
import DescriptionList, {
  DescriptionListDisplayMode,
} from "core/components/DescriptionList";
import Link from "core/components/Link";
import Page from "core/components/Page";
import Switch from "core/components/Switch";
import Time from "core/components/Time";
import User from "core/features/User";
import { createGetServerSideProps } from "core/helpers/page";
import { formatDuration } from "core/helpers/time";
import { NextPageWithLayout } from "core/helpers/types";
import useInterval from "core/hooks/useInterval";
import {
  PipelineParameter,
  PipelineRunStatus,
  PipelineRunTrigger,
  PipelineType,
} from "graphql/types";
import isNil from "lodash/isNil";
import { DateTime } from "luxon";
import { useTranslation } from "next-i18next";
import PipelineRunStatusBadge from "pipelines/features/PipelineRunStatusBadge";
import RunLogs from "pipelines/features/RunLogs";
import RunMessages from "pipelines/features/RunMessages";
import { useCallback, useMemo, useState } from "react";
import RunOutputsTable from "workspaces/features/RunOutputsTable";
import RunPipelineDialog from "workspaces/features/RunPipelineDialog";
import StopPipelineDialog from "workspaces/features/StopPipelineDialog";
import {
  useWorkspacePipelineRunPageQuery,
  WorkspacePipelineRunPageDocument,
  WorkspacePipelineRunPageQuery,
  WorkspacePipelineRunPageQueryVariables,
} from "workspaces/graphql/queries.generated";
import {
  formatPipelineType,
  getPipelineRunConfig,
  isConnectionParameter,
} from "workspaces/helpers/pipelines";
import WorkspaceLayout from "workspaces/layouts/WorkspaceLayout";

type Props = {
  workspaceSlug: string;
  runId: string;
};

const WorkspacePipelineRunPage: NextPageWithLayout = (props: Props) => {
  const { t } = useTranslation();
  const { data, refetch } = useWorkspacePipelineRunPageQuery({
    variables: { workspaceSlug: props.workspaceSlug, runId: props.runId },
  });

  const config = useMemo(
    () => (data?.pipelineRun ? getPipelineRunConfig(data.pipelineRun) : []),
    [data],
  );

  const refreshInterval = useMemo(() => {
    switch (data?.pipelineRun?.status) {
      case PipelineRunStatus.Queued:
      case PipelineRunStatus.Terminating:
        return 0.5 * 1000; // 2 times per second
      case PipelineRunStatus.Running:
        return 0.25 * 1000; // 4 times per second
      default:
        return null;
    }
  }, [data]);

  const [isStopPipelineDialogOpen, setIsStopPipelineDialogOpen] =
    useState(false);

  useInterval(useCallback(refetch, [refetch]), refreshInterval);

  const isFinished =
    data?.pipelineRun &&
    [
      PipelineRunStatus.Failed,
      PipelineRunStatus.Success,
      PipelineRunStatus.Stopped,
    ].includes(data.pipelineRun.status);

  if (!data?.workspace || !data.pipelineRun) {
    return null;
  }
  const { workspace, pipelineRun: run } = data;
  const hasOutputs = run.datasetVersions.length + run.outputs.length > 0;

  const renderParameterValue = (entry: PipelineParameter & { value: any }) => {
    if (entry.type === "str" && entry.value) {
      return entry.multiple ? entry.value.join(", ") : entry.value;
    }
    if (entry.type === "bool") {
      return <Switch checked={entry.value} disabled />;
    }
    if (
      (entry.type === "int" || entry.type === "float") &&
      !isNil(entry.value)
    ) {
      return entry.multiple ? entry.value.join(", ") : entry.value;
    }
    if (isConnectionParameter(entry.type) && entry.value) {
      return entry.value;
    }
    if (entry.type === "dataset") {
      return (
        <Link
          href={`/workspaces/${encodeURIComponent(
            workspace.slug,
          )}/datasets/${encodeURIComponent(entry.value)}`}
        >
          {entry.value}
        </Link>
      );
    }

    return "-";
  };

  return (
    <Page title={run.pipeline.name ?? t("Pipeline run")}>
      <WorkspaceLayout
        workspace={workspace}
        helpLinks={[
          {
            label: t("About pipelines"),
            href: "https://github.com/BLSQ/openhexa/wiki/User-manual#using-pipelines",
          },
          {
            label: t("Writing OpenHEXA pipelines"),
            href: "https://github.com/BLSQ/openhexa/wiki/Writing-OpenHEXA-pipelines",
          },
        ]}
        header={
          <>
            <Breadcrumbs withHome={false}>
              <Breadcrumbs.Part
                isFirst
                href={`/workspaces/${encodeURIComponent(workspace.slug)}`}
              >
                {workspace.name}
              </Breadcrumbs.Part>
              <Breadcrumbs.Part
                href={`/workspaces/${encodeURIComponent(
                  workspace.slug,
                )}/pipelines`}
              >
                {t("Pipelines")}
              </Breadcrumbs.Part>
              <Breadcrumbs.Part
                href={`/workspaces/${encodeURIComponent(
                  workspace.slug,
                )}/pipelines/${encodeURIComponent(run.pipeline.code)}`}
              >
                {run.pipeline.name}
              </Breadcrumbs.Part>
              <Breadcrumbs.Part
                href={`/workspaces/${encodeURIComponent(
                  workspace.slug,
                )}/pipelines/${encodeURIComponent(run.pipeline.code)}/runs`}
              >
                {t("Runs")}
              </Breadcrumbs.Part>
              <Breadcrumbs.Part
                isLast
                href={{
                  pathname:
                    "/workspaces/[workspaceSlug]/pipelines/[pipelineCode]/runs/[runId]",
                  query: {
                    workspaceSlug: workspace.slug,
                    pipelineCode: run.pipeline.code,
                    runId: run.id,
                  },
                }}
              >
                <Time datetime={run.executionDate} />
              </Breadcrumbs.Part>
            </Breadcrumbs>
            {isFinished && (
              <RunPipelineDialog pipeline={run.pipeline} run={run}>
                {(onClick) => (
                  <Button
                    leadingIcon={<ArrowPathIcon className="h-4 w-4" />}
                    onClick={onClick}
                  >
                    {t("Run again")}
                  </Button>
                )}
              </RunPipelineDialog>
            )}
            {!isFinished && run.pipeline.permissions.stopPipeline && (
              <Button
                leadingIcon={<StopIcon className="h-4 w-4" />}
                className="bg-red-500 hover:bg-red-700 focus:ring-red-500"
                onClick={() => setIsStopPipelineDialogOpen(true)}
              >
                {t("Stop")}
              </Button>
            )}
          </>
        }
      >
        <WorkspaceLayout.PageContent>
          <Block className="divide-y-2 divide-gray-100">
            <Block.Header>
              <div className="flex items-center gap-4">
                <div className="truncate">
                  <Time
                    datetime={run.executionDate}
                    className="truncate text-sm font-medium text-gray-900"
                  />
                  <div className="mt-1.5 text-sm font-normal text-gray-500">
                    {run.status === PipelineRunStatus.Success &&
                      t("Succeeded on {{relativeTime}}", {
                        relativeTime: DateTime.fromISO(
                          run.executionDate,
                        ).toLocaleString(DateTime.DATETIME_SHORT),
                      })}
                    {run.status === PipelineRunStatus.Failed &&
                      t("Failed on {{relativeTime}}", {
                        relativeTime: DateTime.fromISO(
                          run.executionDate,
                        ).toLocaleString(DateTime.DATETIME_SHORT),
                      })}
                    {run.status === PipelineRunStatus.Queued &&
                      t("Queued on {{relativeTime}}", {
                        relativeTime: DateTime.fromISO(
                          run.executionDate,
                        ).toLocaleString(DateTime.DATETIME_SHORT),
                      })}
                    {run.status === PipelineRunStatus.Running &&
                      t("Started on {{relativeTime}}", {
                        relativeTime: DateTime.fromISO(
                          run.executionDate,
                        ).toLocaleString(DateTime.DATETIME_SHORT),
                      })}
                    {run.status === PipelineRunStatus.Stopped &&
                      t("Stopped on {{relativeTime}}", {
                        relativeTime: DateTime.fromISO(
                          run.executionDate,
                        ).toLocaleString(DateTime.DATETIME_SHORT),
                      })}
                  </div>
                </div>
                <div className="flex items-center gap-4">
                  <div
                    title={run.executionDate}
                    suppressHydrationWarning={true}
                  >
                    <PipelineRunStatusBadge run={run} />
                  </div>
                </div>
              </div>
            </Block.Header>
            <Block.Section>
              <DescriptionList>
                <DescriptionList.Item label={t("Pipeline")}>
                  <Link
                    href={`/workspaces/${encodeURIComponent(
                      workspace.slug,
                    )}/pipelines/${encodeURIComponent(run.pipeline.code)}`}
                  >
                    {run.pipeline.name}
                  </Link>
                </DescriptionList.Item>
                <DescriptionList.Item label={t("Execution Date")}>
                  <Time datetime={run.executionDate} />
                </DescriptionList.Item>
                <DescriptionList.Item label={t("Type")}>
                  <Badge>{formatPipelineType(run.pipeline.type)}</Badge>
                </DescriptionList.Item>
                {run.pipeline.type === PipelineType.Notebook && (
                  <DescriptionList.Item label={t("Notebook")}>
                    <code>{run.pipeline.notebookPath}</code>
                  </DescriptionList.Item>
                )}
                <DescriptionList.Item label={t("Trigger")}>
                  {run.triggerMode === PipelineRunTrigger.Manual && t("Manual")}
                  {run.triggerMode === PipelineRunTrigger.Scheduled &&
                    t("Scheduled")}
                  {run.triggerMode === PipelineRunTrigger.Webhook &&
                    t("Webhook")}
                </DescriptionList.Item>
                <DescriptionList.Item label={t("User")}>
                  {run.user ? <User user={run.user} /> : "-"}
                </DescriptionList.Item>
                {run.duration ? (
                  <DescriptionList.Item label={t("Duration")}>
                    {formatDuration(run.duration)}
                  </DescriptionList.Item>
                ) : null}
                {run.stoppedBy && (
                  <DescriptionList.Item label={t("Stopped by")}>
                    <User user={run.stoppedBy} />
                  </DescriptionList.Item>
                )}
                {run.version && (
                  <DescriptionList.Item label={t("Version")}>
                    {run.version.versionName}
                  </DescriptionList.Item>
                )}
                <DescriptionList.Item
                  label={t("Timeout")}
                  help={t("See documentation for more info.")}
                >
                  {run.timeout ? formatDuration(run.timeout) : "-"}
                </DescriptionList.Item>
              </DescriptionList>
            </Block.Section>
            {run.pipeline.type === PipelineType.ZipFile && (
              <Block.Section title={t("Parameters")}>
                <DescriptionList
                  columns={2}
                  displayMode={DescriptionListDisplayMode.LABEL_ABOVE}
                >
                  {config.map((entry) => (
                    <DescriptionList.Item key={entry.name} label={entry.name}>
                      {renderParameterValue(entry)}
                    </DescriptionList.Item>
                  ))}
                </DescriptionList>
              </Block.Section>
            )}

            {isFinished && (
              <Block.Section title={"Outputs"}>
                {hasOutputs ? (
                  <RunOutputsTable workspace={workspace} run={run} />
                ) : (
                  <p className="text-sm italic text-gray-600">
                    {t("No outputs")}
                  </p>
                )}
              </Block.Section>
            )}
            <Block.Section title={t("Messages")}>
              {/* Set a ref to the component to recreate it completely when the run id changes.  */}
              <RunMessages key={run.id} run={run} />
            </Block.Section>
            <Block.Section title={t("Logs")} collapsible defaultOpen={false}>
              <RunLogs run={run} />
            </Block.Section>
          </Block>
        </WorkspaceLayout.PageContent>
      </WorkspaceLayout>
      <StopPipelineDialog
        open={isStopPipelineDialogOpen}
        pipeline={run.pipeline}
        onClose={() => setIsStopPipelineDialogOpen(false)}
        run={run}
      />
    </Page>
  );
};

WorkspacePipelineRunPage.getLayout = (page) => page;

export const getServerSideProps = createGetServerSideProps({
  requireAuth: true,
  async getServerSideProps(ctx, client) {
    await WorkspaceLayout.prefetch(ctx, client);
    const { data } = await client.query<
      WorkspacePipelineRunPageQuery,
      WorkspacePipelineRunPageQueryVariables
    >({
      query: WorkspacePipelineRunPageDocument,
      variables: {
        workspaceSlug: ctx.params?.workspaceSlug as string,
        runId: ctx.params?.runId as string,
      },
    });

    if (!data.workspace || !data.pipelineRun) {
      return {
        notFound: true,
      };
    }
    return {
      props: {
        workspaceSlug: ctx.params?.workspaceSlug as string,
        runId: ctx.params?.runId as string,
      },
    };
  },
});

export default WorkspacePipelineRunPage;

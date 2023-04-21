import Block from "core/components/Block";
import Breadcrumbs from "core/components/Breadcrumbs";
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
import { PipelineRunStatus, PipelineRunTrigger } from "graphql-types";
import { DateTime } from "luxon";
import { useTranslation } from "next-i18next";
import { useRouter } from "next/router";
import PipelineRunStatusBadge from "pipelines/features/PipelineRunStatusBadge";
import RunLogs from "pipelines/features/RunLogs";
import RunMessages from "pipelines/features/RunMessages";
import { useCallback, useMemo, useState } from "react";
import useInterval from "core/hooks/useInterval";
import {
  useWorkspacePipelineRunPageQuery,
  WorkspacePipelineRunPageDocument,
  WorkspacePipelineRunPageQuery,
  WorkspacePipelineRunPageQueryVariables,
} from "workspaces/graphql/queries.generated";
import { getPipelineRunConfig } from "workspaces/helpers/pipelines";
import WorkspaceLayout from "workspaces/layouts/WorkspaceLayout";
import Button from "core/components/Button";
import { ArrowPathIcon } from "@heroicons/react/24/outline";
import RunPipelineDialog from "workspaces/features/RunPipelineDialog";
import RunOutputsTable from "workspaces/features/RunOutputsTable";

type Props = {
  workspaceSlug: string;
  runId: string;
};

const WorkspacePipelineRunPage: NextPageWithLayout = (props: Props) => {
  const { t } = useTranslation();
  const router = useRouter();
  const { data, refetch } = useWorkspacePipelineRunPageQuery({
    variables: { workspaceSlug: props.workspaceSlug, runId: props.runId },
  });

  const config = useMemo(
    () => (data?.pipelineRun ? getPipelineRunConfig(data.pipelineRun) : []),
    [data]
  );

  const refreshInterval = useMemo(() => {
    switch (data?.pipelineRun?.status) {
      case PipelineRunStatus.Queued:
        return 1 * 1000;
      case PipelineRunStatus.Running:
        return 3 * 1000;
      default:
        return null;
    }
  }, [data]);

  const onRefetch = useCallback(() => {
    refetch();
  }, [refetch]);
  const [isRunPipelineDialogOpen, setIsRunPipelineDialogOpen] = useState(false);

  useInterval(onRefetch, refreshInterval);

  if (!data?.workspace || !data.pipelineRun) {
    return null;
  }
  const { workspace, pipelineRun: run } = data;
  const isFinished = [
    PipelineRunStatus.Failed,
    PipelineRunStatus.Success,
  ].includes(run.status);

  return (
    <Page title={t("Workspace")}>
      <WorkspaceLayout workspace={workspace}>
        <WorkspaceLayout.Header className="flex items-center justify-between gap-2">
          <Breadcrumbs withHome={false}>
            <Breadcrumbs.Part
              isFirst
              href={`/workspaces/${encodeURIComponent(workspace.slug)}`}
            >
              {workspace.name}
            </Breadcrumbs.Part>
            <Breadcrumbs.Part
              href={`/workspaces/${encodeURIComponent(
                workspace.slug
              )}/pipelines`}
            >
              {t("Pipelines")}
            </Breadcrumbs.Part>
            <Breadcrumbs.Part
              href={`/workspaces/${encodeURIComponent(
                workspace.slug
              )}/pipelines/${encodeURIComponent(run.pipeline.code)}`}
            >
              {run.pipeline.name}
            </Breadcrumbs.Part>
            <Breadcrumbs.Part
              isLast
              href={{
                pathname: "/pipelines/[pipelineCode]/runs/[runId]",
                query: { pipelineCode: run.pipeline.code, runId: run.id },
              }}
            >
              <Time datetime={run.executionDate} />
            </Breadcrumbs.Part>
          </Breadcrumbs>
          <Button
            leadingIcon={<ArrowPathIcon className="h-4 w-4" />}
            onClick={() => setIsRunPipelineDialogOpen(true)}
          >
            {t("Run again")}
          </Button>
        </WorkspaceLayout.Header>

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
                          run.executionDate
                        ).toLocaleString(DateTime.DATETIME_SHORT),
                      })}
                    {run.status === PipelineRunStatus.Failed &&
                      t("Failed on {{relativeTime}}", {
                        relativeTime: DateTime.fromISO(
                          run.executionDate
                        ).toLocaleString(DateTime.DATETIME_SHORT),
                      })}
                    {run.status === PipelineRunStatus.Queued &&
                      t("Queued on {{relativeTime}}", {
                        relativeTime: DateTime.fromISO(
                          run.executionDate
                        ).toLocaleString(DateTime.DATETIME_SHORT),
                      })}
                    {run.status === PipelineRunStatus.Running &&
                      t("Started on {{relativeTime}}", {
                        relativeTime: DateTime.fromISO(
                          run.executionDate
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
                      workspace.slug
                    )}/pipelines/${encodeURIComponent(run.pipeline.code)}`}
                  >
                    {run.pipeline.name}
                  </Link>
                </DescriptionList.Item>
                <DescriptionList.Item label={t("Execution Date")}>
                  <Time datetime={run.executionDate} />
                </DescriptionList.Item>
                <DescriptionList.Item label={t("Trigger")}>
                  {run.triggerMode === PipelineRunTrigger.Manual
                    ? t("Manual")
                    : t("Scheduled")}
                </DescriptionList.Item>
                <DescriptionList.Item label={t("User")}>
                  {run.user ? <User user={run.user} /> : "-"}
                </DescriptionList.Item>
                {run.duration ? (
                  <DescriptionList.Item label={t("Duration")}>
                    {formatDuration(run.duration)}
                  </DescriptionList.Item>
                ) : null}
                <DescriptionList.Item label={t("Version")}>
                  {run.version.number}
                </DescriptionList.Item>
              </DescriptionList>
            </Block.Section>
            <Block.Section title={t("Parameters")}>
              <DescriptionList
                columns={2}
                displayMode={DescriptionListDisplayMode.LABEL_ABOVE}
              >
                {config.map((entry) => (
                  <DescriptionList.Item key={entry.name} label={entry.name}>
                    {(entry.type === "str" && entry.value) ?? "-"}
                    {entry.type === "bool" && (
                      <Switch checked={entry.value} disabled />
                    )}
                    {(entry.type === "int" && entry.value) ?? "-"}
                    {(entry.type === "float" && entry.value) ?? "-"}
                  </DescriptionList.Item>
                ))}
              </DescriptionList>
            </Block.Section>

            {isFinished && (
              <Block.Section title={"Outputs"}>
                {run.outputs.length > 0 ? (
                  <RunOutputsTable workspace={workspace} run={run} />
                ) : (
                  <p className="text-sm italic text-gray-600">
                    {t("No outputs")}
                  </p>
                )}
              </Block.Section>
            )}
            <Block.Section title={t("Messages")}>
              <RunMessages run={run} />
            </Block.Section>
            <Block.Section title={t("Logs")} collapsible>
              <RunLogs run={run} />
            </Block.Section>
          </Block>
        </WorkspaceLayout.PageContent>
      </WorkspaceLayout>
      <RunPipelineDialog
        open={isRunPipelineDialogOpen}
        onClose={() => setIsRunPipelineDialogOpen(false)}
        pipeline={run.pipeline}
        run={run}
      />
    </Page>
  );
};

WorkspacePipelineRunPage.getLayout = (page) => page;

export const getServerSideProps = createGetServerSideProps({
  requireAuth: true,
  async getServerSideProps(ctx, client) {
    await WorkspaceLayout.prefetch(client);

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

import DataGrid, { BaseColumn } from "core/components/DataGrid";
import ChevronLinkColumn from "core/components/DataGrid/ChevronLinkColumn";
import { TextColumn } from "core/components/DataGrid/TextColumn";
import UserColumn from "core/components/DataGrid/UserColumn";
import Link from "core/components/Link";
import Page from "core/components/Page";
import Time from "core/components/Time";
import Tooltip from "core/components/Tooltip";
import { createGetServerSideProps } from "core/helpers/page";
import { formatDuration } from "core/helpers/time";
import { NextPageWithLayout } from "core/helpers/types";
import { PipelineParameter, PipelineRunTrigger, PipelineType } from "graphql/types";
import isNil from "lodash/isNil";
import { useTranslation } from "next-i18next";
import router from "next/router";
import PipelineRunStatusBadge from "pipelines/features/PipelineRunStatusBadge";
import {
  useWorkspacePipelineRunsPageQuery,
  WorkspacePipelineRunsPageDocument,
  WorkspacePipelineRunsPageQuery,
  WorkspacePipelineRunsPageQueryVariables,
} from "workspaces/graphql/queries.generated";
import { getPipelineRunConfig, isConnectionParameter } from "workspaces/helpers/pipelines";
import PipelineLayout from "workspaces/layouts/PipelineLayout";

function formatParamValue(entry: PipelineParameter & { value: any }): string {
  if (entry.type === "bool") return entry.value ? "✓" : "✗";
  if (entry.type === "secret" && entry.value) return "••••••";
  if (isNil(entry.value)) return "-";
  if (entry.multiple && Array.isArray(entry.value)) return entry.value.join(", ");
  if (isConnectionParameter(entry.type)) return String(entry.value);
  return String(entry.value);
}

function RunParametersCell({
  run,
}: {
  run: { config: any; version?: { parameters: Omit<PipelineParameter, "__typename">[] } | null };
}) {
  const params = getPipelineRunConfig(run);
  if (!params.length) return <span className="text-gray-400">-</span>;

  const tooltipContent = (
    <div className="min-w-48 space-y-1">
      {params.map((p) => (
        <div key={p.code} className="flex gap-1">
          <span className="shrink-0 font-medium text-gray-500">{p.name}:</span>
          <span className="break-all">{formatParamValue(p)}</span>
        </div>
      ))}
    </div>
  );

  return (
    <Tooltip label={tooltipContent} placement="left">
      <div className="max-h-16 cursor-default space-y-0.5 overflow-hidden text-xs text-gray-600">
        {params.map((p) => (
          <div key={p.code} className="flex min-w-0 gap-1">
            <span className="shrink-0 text-gray-400">{p.name}:</span>
            <span className="truncate">{formatParamValue(p)}</span>
          </div>
        ))}
      </div>
    </Tooltip>
  );
}

type Props = {
  page: number;
  perPage: number;
  pipelineCode: string;
  workspaceSlug: string;
};

const WorkspacePipelineRunsPage: NextPageWithLayout = (props: Props) => {
  const { pipelineCode, workspaceSlug, page, perPage } = props;
  const { t } = useTranslation();
  const { data } = useWorkspacePipelineRunsPageQuery({
    variables: {
      workspaceSlug,
      pipelineCode,
      page,
      perPage,
    },
  });

  if (!data?.workspace || !data?.pipeline) {
    return null;
  }

  const { workspace, pipeline } = data;

  return (
    <Page title={pipeline.name ?? t("Pipeline runs")}>
      <PipelineLayout
        workspace={workspace}
        pipeline={pipeline}
        currentTab="runs"
        extraBreadcrumbs={[
          {
            title: t("Runs"),
            href: `/workspaces/${encodeURIComponent(
              workspace.slug,
            )}/pipelines/${encodeURIComponent(pipeline.code)}/runs`,
          },
        ]}
      >
        <DataGrid
          defaultPageSize={perPage}
          defaultPageIndex={page - 1}
          data={pipeline.runs.items}
          totalItems={pipeline.runs.totalItems}
          fixedLayout={false}
          fetchData={({ page, pageSize }) => {
            router.push({
              pathname: router.pathname,
              query: {
                ...router.query,
                page,
                perPage: pageSize,
              },
            });
          }}
        >
          <BaseColumn id="name" label={t("Executed on")}>
            {(item) => (
              <Link
                customStyle="text-gray-700 font-medium"
                href={{
                  pathname:
                    "/workspaces/[workspaceSlug]/pipelines/[pipelineCode]/runs/[runId]",
                  query: {
                    pipelineCode: pipeline.code,
                    workspaceSlug: workspace.slug,
                    runId: item.id,
                  },
                }}
              >
                <Time datetime={item.executionDate} />
              </Link>
            )}
          </BaseColumn>
          <BaseColumn<PipelineRunTrigger>
            label={t("Trigger")}
            accessor="triggerMode"
          >
            {(value) => (
              <span>
                {value === PipelineRunTrigger.Scheduled && t("Scheduled")}
                {value === PipelineRunTrigger.Manual && t("Manual")}
                {value === PipelineRunTrigger.Webhook && t("Webhook")}
              </span>
            )}
          </BaseColumn>
          <BaseColumn label={t("Status")} id="status">
            {(item) => <PipelineRunStatusBadge run={item} />}
          </BaseColumn>
          {pipeline.type === PipelineType.ZipFile ? (
            <TextColumn accessor="version.versionName" label={t("Version")} />
          ) : null}
          <BaseColumn label={t("Duration")} accessor="duration">
            {(value) => (
              <span suppressHydrationWarning>
                {value ? formatDuration(value) : "-"}
              </span>
            )}
          </BaseColumn>
          <UserColumn label={t("User")} accessor="user" />
          <BaseColumn label={t("Parameters")} id="parameters">
            {(item) => <RunParametersCell run={item} />}
          </BaseColumn>
          <ChevronLinkColumn
            accessor="id"
            url={(value: any) => ({
              pathname:
                "/workspaces/[workspaceSlug]/pipelines/[pipelineCode]/runs/[runId]",
              query: {
                workspaceSlug: workspace.slug,
                pipelineCode: pipeline.code,
                runId: value,
              },
            })}
          />
        </DataGrid>
      </PipelineLayout>
    </Page>
  );
};

WorkspacePipelineRunsPage.getLayout = (page) => page;

export const getServerSideProps = createGetServerSideProps({
  requireAuth: true,
  async getServerSideProps(ctx, client) {
    await PipelineLayout.prefetch(ctx, client);

    const page = parseInt(ctx.query.page as string, 10) || 1;
    const perPage = parseInt(ctx.query.perPage as string, 10) || 15;
    const { data } = await client.query<
      WorkspacePipelineRunsPageQuery,
      WorkspacePipelineRunsPageQueryVariables
    >({
      query: WorkspacePipelineRunsPageDocument,
      variables: {
        workspaceSlug: ctx.params!.workspaceSlug as string,
        pipelineCode: ctx.params!.pipelineCode as string,
        page,
        perPage,
      },
    });

    if (!data.workspace || !data.pipeline) {
      return { notFound: true };
    }
    return {
      props: {
        workspaceSlug: ctx.params!.workspaceSlug,
        pipelineCode: ctx.params!.pipelineCode,
        page,
        perPage,
      },
    };
  },
});

export default WorkspacePipelineRunsPage;

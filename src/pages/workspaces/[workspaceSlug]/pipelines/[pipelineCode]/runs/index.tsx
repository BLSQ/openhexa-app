import DataGrid, { BaseColumn } from "core/components/DataGrid";
import ChevronLinkColumn from "core/components/DataGrid/ChevronLinkColumn";
import { TextColumn } from "core/components/DataGrid/TextColumn";
import UserColumn from "core/components/DataGrid/UserColumn";
import Link from "core/components/Link";
import Page from "core/components/Page";
import Time from "core/components/Time";
import { createGetServerSideProps } from "core/helpers/page";
import { formatDuration } from "core/helpers/time";
import { NextPageWithLayout } from "core/helpers/types";
import { PipelineRunTrigger, PipelineType } from "graphql/types";
import { useTranslation } from "next-i18next";
import router from "next/router";
import PipelineRunStatusBadge from "pipelines/features/PipelineRunStatusBadge";
import {
  useWorkspacePipelineRunsPageQuery,
  WorkspacePipelineRunsPageDocument,
  WorkspacePipelineRunsPageQuery,
  WorkspacePipelineRunsPageQueryVariables,
} from "workspaces/graphql/queries.generated";
import PipelineLayout from "workspaces/layouts/PipelineLayout";

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

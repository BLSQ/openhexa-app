import Breadcrumbs from "core/components/Breadcrumbs";
import Page from "core/components/Page";
import Pagination from "core/components/Pagination";
import { createGetServerSideProps } from "core/helpers/page";
import { NextPageWithLayout } from "core/helpers/types";
import useCacheKey from "core/hooks/useCacheKey";
import { useTranslation } from "next-i18next";
import { useRouter } from "next/router";
import PipelineVersionCard from "pipelines/features/PipelineVersionCard";
import {
  useWorkspacePipelineVersionsPageQuery,
  WorkspacePipelineVersionsPageDocument,
  WorkspacePipelineVersionsPageQuery,
  WorkspacePipelineVersionsPageQueryVariables,
} from "workspaces/graphql/queries.generated";
import WorkspaceLayout from "workspaces/layouts/WorkspaceLayout";

type Props = {
  workspaceSlug: string;
  pipelineCode: string;
  page: number;
  perPage: number;
};
const PipelineVersionsPage: NextPageWithLayout<Props> = ({
  workspaceSlug,
  pipelineCode,
  page,
  perPage,
}) => {
  const { t } = useTranslation();

  const { data, refetch } = useWorkspacePipelineVersionsPageQuery({
    variables: {
      workspaceSlug,
      pipelineCode,
      page,
      perPage,
    },
  });

  useCacheKey(["pipelines", data?.pipeline?.id], refetch);

  const router = useRouter();
  if (!data?.workspace || !data?.pipeline) {
    return null;
  }

  const { workspace, pipeline } = data;
  return (
    <Page title={t("Versions of {{pipeline}}", { pipeline: pipeline.name })}>
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
          <div className="flex items-center gap-2">
            <Breadcrumbs withHome={false} className="flex-1">
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
                )}/pipelines/${encodeURIComponent(pipeline.code)}`}
              >
                {pipeline.name}
              </Breadcrumbs.Part>
              <Breadcrumbs.Part
                isLast
                href={`/workspaces/${encodeURIComponent(
                  workspace.slug,
                )}/pipelines/${encodeURIComponent(pipeline.code)}/versions`}
              >
                {t("Versions")}
              </Breadcrumbs.Part>
            </Breadcrumbs>
          </div>
        }
      >
        <WorkspaceLayout.PageContent className="grid grid-cols-1 gap-4">
          {data.pipeline.versions.items.length === 0 && (
            <div className="text-center text-gray-500">
              <div>{t("This pipeline does not have any version.")}</div>
            </div>
          )}
          {data.pipeline.versions.items.map((version) => (
            <PipelineVersionCard key={version.id} version={version} />
          ))}
          <Pagination
            totalItems={data.pipeline.versions.totalItems}
            page={page}
            perPage={perPage}
            countItems={data.pipeline.versions.items.length}
            onChange={(page) =>
              router.push({
                pathname: router.pathname,
                query: {
                  ...router.query,
                  page,
                },
              })
            }
          />
        </WorkspaceLayout.PageContent>
      </WorkspaceLayout>
    </Page>
  );
};

PipelineVersionsPage.getLayout = (page) => page;

export const getServerSideProps = createGetServerSideProps({
  requireAuth: true,
  async getServerSideProps(ctx, client) {
    await WorkspaceLayout.prefetch(ctx, client);
    const page = parseInt(ctx.query.page as string, 10) || 1;
    const PER_PAGE = 15;
    const { data } = await client.query<
      WorkspacePipelineVersionsPageQuery,
      WorkspacePipelineVersionsPageQueryVariables
    >({
      query: WorkspacePipelineVersionsPageDocument,
      variables: {
        workspaceSlug: ctx.params!.workspaceSlug as string,
        pipelineCode: ctx.params!.pipelineCode as string,
        page,
        perPage: PER_PAGE,
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
        perPage: PER_PAGE,
      },
    };
  },
});

export default PipelineVersionsPage;

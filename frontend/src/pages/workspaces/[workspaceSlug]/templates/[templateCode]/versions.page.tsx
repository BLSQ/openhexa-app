import Breadcrumbs from "core/components/Breadcrumbs";
import Page from "core/components/Page";
import Pagination from "core/components/Pagination";
import { createGetServerSideProps } from "core/helpers/page";
import { NextPageWithLayout } from "core/helpers/types";
import useCacheKey from "core/hooks/useCacheKey";
import { useTranslation } from "next-i18next";
import { useRouter } from "next/router";
import {
  useWorkspaceTemplateVersionsPageQuery,
  WorkspaceTemplateVersionsPageDocument,
  WorkspaceTemplateVersionsPageQuery,
  WorkspaceTemplateVersionsPageQueryVariables,
} from "workspaces/graphql/queries.generated";
import WorkspaceLayout from "workspaces/layouts/WorkspaceLayout";
import TemplateVersionCard from "pipelines/features/TemplateVersionCard";

type Props = {
  workspaceSlug: string;
  templateCode: string;
  page: number;
  perPage: number;
};
const TemplateVersionsPage: NextPageWithLayout<Props> = ({
  workspaceSlug,
  templateCode,
  page,
  perPage,
}) => {
  const { t } = useTranslation();

  const { data, refetch } = useWorkspaceTemplateVersionsPageQuery({
    variables: {
      workspaceSlug,
      templateCode,
      page,
      perPage,
    },
  });

  useCacheKey(["templates", data?.template?.id], refetch);

  const router = useRouter();
  if (!data?.workspace || !data?.template) {
    return null;
  }

  const { workspace, template } = data;
  return (
    <Page title={t("Versions of {{template}}", { template: template.name })}>
      <WorkspaceLayout
        workspace={workspace}
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
                )}/pipelines/?tab=templates`}
              >
                {t("Templates")}
              </Breadcrumbs.Part>

              <Breadcrumbs.Part
                href={`/workspaces/${encodeURIComponent(
                  workspace.slug,
                )}/templates/${encodeURIComponent(template.code)}`}
              >
                {template.name}
              </Breadcrumbs.Part>
              <Breadcrumbs.Part
                isLast
                href={`/workspaces/${encodeURIComponent(
                  workspace.slug,
                )}/templates/${encodeURIComponent(template.code)}/versions`}
              >
                {t("Versions")}
              </Breadcrumbs.Part>
            </Breadcrumbs>
          </div>
        }
      >
        <WorkspaceLayout.PageContent className="grid grid-cols-1 gap-4">
          {data.template.versions.items.length === 0 && (
            <div className="text-center text-gray-500">
              <div>{t("This pipeline does not have any version.")}</div>
            </div>
          )}
          {data.template.versions.items.map((version) => (
            <TemplateVersionCard key={version.id} version={version} />
          ))}
          <Pagination
            totalItems={data.template.versions.totalItems}
            page={page}
            perPage={perPage}
            countItems={data.template.versions.items.length}
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

TemplateVersionsPage.getLayout = (page) => page;

export const getServerSideProps = createGetServerSideProps({
  requireAuth: true,
  async getServerSideProps(ctx, client) {
    await WorkspaceLayout.prefetch(ctx, client);
    const page = parseInt(ctx.query.page as string, 10) || 1;
    const PER_PAGE = 15;
    const { data } = await client.query<
      WorkspaceTemplateVersionsPageQuery,
      WorkspaceTemplateVersionsPageQueryVariables
    >({
      query: WorkspaceTemplateVersionsPageDocument,
      variables: {
        workspaceSlug: ctx.params!.workspaceSlug as string,
        templateCode: ctx.params!.templateCode as string,
        page,
        perPage: PER_PAGE,
      },
    });

    if (!data.workspace || !data.template) {
      return { notFound: true };
    }
    return {
      props: {
        workspaceSlug: ctx.params!.workspaceSlug,
        templateCode: ctx.params!.templateCode,
        page,
        perPage: PER_PAGE,
      },
    };
  },
});

export default TemplateVersionsPage;

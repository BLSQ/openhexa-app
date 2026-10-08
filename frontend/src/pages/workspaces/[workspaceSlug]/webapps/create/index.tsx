import WebappForm from "webapps/features/WebappForm";
import { createGetServerSideProps } from "core/helpers/page";
import {
  WorkspacePageDocument,
  WorkspacePageQuery,
} from "workspaces/graphql/queries.generated";
import Breadcrumbs from "core/components/Breadcrumbs";
import WorkspaceLayout from "workspaces/layouts/WorkspaceLayout";
import Page from "core/components/Page";
import { useTranslation } from "next-i18next";
import { WebappType } from "graphql/types";

const WebappCreatePage = ({ workspace, defaultType }: any) => {
  const { t } = useTranslation();

  return (
    <Page title={t("Web Apps")}>
      <WorkspaceLayout
        workspace={workspace}
        header={
          <Breadcrumbs withHome={false} className="flex-1">
            <Breadcrumbs.Part
              isFirst
              href={`/workspaces/${encodeURIComponent(workspace.slug)}/webapps`}
            >
              {t("Web Apps")}
            </Breadcrumbs.Part>
            <Breadcrumbs.Part
              href={`/workspaces/${encodeURIComponent(
                workspace.slug,
              )}/webapps/create`}
              isLast
            >
              {t("Create")}
            </Breadcrumbs.Part>
          </Breadcrumbs>
        }
      >
        <WorkspaceLayout.PageContent>
          <WebappForm workspace={workspace} defaultType={defaultType} />
        </WorkspaceLayout.PageContent>
      </WorkspaceLayout>
    </Page>
  );
};

export const getServerSideProps = createGetServerSideProps({
  requireAuth: true,
  getServerSideProps: async (ctx, client) => {
    await WorkspaceLayout.prefetch(ctx, client);
    const { data } = await client.query<WorkspacePageQuery>({
      query: WorkspacePageDocument,
      variables: {
        slug: ctx.params?.workspaceSlug as string,
      },
    });
    if (!data.workspace) {
      return { notFound: true };
    }
    if (!data.workspace.permissions.update) {
      return {
        redirect: {
          permanent: false,
          destination: `/workspaces/${encodeURIComponent(
            data.workspace.slug,
          )}/webapps`,
        },
      };
    }
    const type = ctx.query?.type as WebappType;
    return {
      props: {
        workspace: data.workspace,
        ...(Object.values(WebappType).includes(type) && { defaultType: type }),
      },
    };
  },
});

export default WebappCreatePage;

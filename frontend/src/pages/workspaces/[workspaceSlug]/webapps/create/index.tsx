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

const WebappCreatePage = ({ workspace }: any) => {
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
          <WebappForm workspace={workspace} />
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
    return {
      props: {
        workspace: data.workspace,
      },
    };
  },
});

export default WebappCreatePage;

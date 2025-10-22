import Page from "core/components/Page";
import { createGetServerSideProps } from "core/helpers/page";
import { NextPageWithLayout } from "core/helpers/types";
import { useTranslation } from "next-i18next";
import {
  WorkspaceWebappPageDocument,
  WorkspaceWebappPageQuery,
  WorkspaceWebappPageQueryVariables,
} from "workspaces/graphql/queries.generated";
import WorkspaceLayout from "workspaces/layouts/WorkspaceLayout";
import Breadcrumbs from "core/components/Breadcrumbs";
import WebappIframe from "webapps/features/WebappIframe";
import { useQuery } from "@apollo/client/react";
import { graphql } from "graphql/gql";

const WorkspaceWebappPageDoc = graphql(`
query WorkspaceWebappPage($workspaceSlug: String!, $webappId: UUID!) {
  workspace(slug: $workspaceSlug) {
    ...WebappForm_workspace
  }
  webapp: webapp(id: $webappId) {
    ...WebappForm_webapp
  }
}
`);

type Props = {
  webappId: string;
  workspaceSlug: string;
};

const WorkspaceWebappPlayPage: NextPageWithLayout = (props: Props) => {
  const { webappId, workspaceSlug } = props;
  const { t } = useTranslation();

  const { data } = useQuery(WorkspaceWebappPageDoc, {
    variables: {
      workspaceSlug,
      webappId,
    },
  });

  if (!data?.workspace || !data?.webapp) {
    return null;
  }

  const { workspace, webapp } = data;

  return (
    <Page title={t("Web Apps")}>
      <WorkspaceLayout
        workspace={workspace}
        header={
          <>
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
                )}/webapps`}
              >
                {t("Web Apps")}
              </Breadcrumbs.Part>
              <Breadcrumbs.Part
                href={`/workspaces/${encodeURIComponent(
                  workspace.slug,
                )}/webapps/${encodeURIComponent(webapp.id)}`}
                isLast
              >
                {webapp.name}
              </Breadcrumbs.Part>
            </Breadcrumbs>
          </>
        }
      >
        <WorkspaceLayout.PageContent>
          <WebappIframe url={webapp.url} />
        </WorkspaceLayout.PageContent>
      </WorkspaceLayout>
    </Page>
  );
};

WorkspaceWebappPlayPage.getLayout = (page) => page;

export const getServerSideProps = createGetServerSideProps({
  requireAuth: true,
  async getServerSideProps(ctx, client) {
    await WorkspaceLayout.prefetch(ctx, client);
    const { data } = await client.query<
      WorkspaceWebappPageQuery,
      WorkspaceWebappPageQueryVariables
    >({
      query: WorkspaceWebappPageDocument,
      variables: {
        workspaceSlug: ctx.params!.workspaceSlug as string,
        webappId: ctx.params!.webappId as string,
      },
    });

    if (!data.workspace || !data.webapp) {
      return { notFound: true };
    }

    return {
      props: {
        workspaceSlug: ctx.params!.workspaceSlug,
        webappId: ctx.params!.webappId,
        workspace: data.workspace,
        webapp: data.webapp,
      },
    };
  },
});

export default WorkspaceWebappPlayPage;

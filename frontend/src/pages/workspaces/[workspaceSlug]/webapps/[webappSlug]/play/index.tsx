import Page from "core/components/Page";
import { createGetServerSideProps } from "core/helpers/page";
import { NextPageWithLayout } from "core/helpers/types";
import { useTranslation } from "next-i18next";
import {
  useWorkspaceWebappPageQuery,
  WorkspaceWebappPageDocument,
  WorkspaceWebappPageQuery,
  WorkspaceWebappPageQueryVariables,
} from "workspaces/graphql/queries.generated";
import {
  usePublicWebappQuery,
  PublicWebappDocument,
  PublicWebappQuery,
  PublicWebappQueryVariables,
} from "webapps/graphql/publicQueries.generated";
import WorkspaceLayout from "workspaces/layouts/WorkspaceLayout";
import Breadcrumbs from "core/components/Breadcrumbs";
import WebappIframe from "webapps/features/WebappIframe";

type Props = {
  webappSlug: string;
  workspaceSlug: string;
  isPublic?: boolean;
};

const WorkspaceWebappPlayPage: NextPageWithLayout = (props: Props) => {
  const { webappSlug, workspaceSlug, isPublic } = props;
  const { t } = useTranslation();

  const publicQueryResult = usePublicWebappQuery({
    variables: { workspaceSlug, webappSlug },
    skip: !isPublic,
  });

  const authenticatedQueryResult = useWorkspaceWebappPageQuery({
    variables: { workspaceSlug, webappSlug },
    skip: isPublic,
  });

  const data = isPublic ? publicQueryResult.data : authenticatedQueryResult.data;

  if (isPublic) {
    const webapp = data?.publicWebapp;
    if (!webapp) return null;

    return (
      <Page title={webapp.name}>
        <div className="h-screen">
          <WebappIframe url={webapp.url ?? undefined} />
        </div>
      </Page>
    );
  }

  if (!data?.workspace || !data?.webapp) {
    return null;
  }

  const { workspace, webapp } = data;

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
              )}/webapps/${encodeURIComponent(webapp.slug)}`}
              isLast
            >
              {webapp.name}
            </Breadcrumbs.Part>
          </Breadcrumbs>
        }
      >
        <WorkspaceLayout.PageContent>
          <WebappIframe url={webapp.url ?? undefined} />
        </WorkspaceLayout.PageContent>
      </WorkspaceLayout>
    </Page>
  );
};

WorkspaceWebappPlayPage.getLayout = (page) => page;

export const getServerSideProps = createGetServerSideProps({
  requireAuth: false,
  async getServerSideProps(ctx, client) {
    const workspaceSlug = ctx.params!.workspaceSlug as string;
    const webappSlug = ctx.params!.webappSlug as string;

    if (ctx.me?.user) {
      await WorkspaceLayout.prefetch(ctx, client);
      const { data } = await client.query<
        WorkspaceWebappPageQuery,
        WorkspaceWebappPageQueryVariables
      >({
        query: WorkspaceWebappPageDocument,
        variables: { workspaceSlug, webappSlug },
      });

      if (!data.workspace || !data.webapp) {
        return { notFound: true };
      }

      return {
        props: {
          workspaceSlug,
          webappSlug,
          workspace: data.workspace,
          webapp: data.webapp,
          isPublic: false,
        },
      };
    }

    const { data } = await client.query<
      PublicWebappQuery,
      PublicWebappQueryVariables
    >({
      query: PublicWebappDocument,
      variables: { workspaceSlug, webappSlug },
    });

    if (!data.publicWebapp) {
      return { notFound: true };
    }

    return {
      props: {
        workspaceSlug,
        webappSlug,
        isPublic: true,
      },
    };
  },
});

export default WorkspaceWebappPlayPage;

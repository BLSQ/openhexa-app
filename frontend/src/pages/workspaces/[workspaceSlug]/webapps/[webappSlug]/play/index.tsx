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

const WorkspaceWebappPlayPage: NextPageWithLayout = (props: Props & { webapp?: any; workspace?: any }) => {
  const { webappSlug, workspaceSlug, isPublic, webapp: initialWebapp, workspace: initialWorkspace } = props;
  const { t } = useTranslation();

  const publicQueryResult = usePublicWebappQuery({
    variables: { workspaceSlug, webappSlug },
    skip: !isPublic || !!initialWebapp,
  });

  const authenticatedQueryResult = useWorkspaceWebappPageQuery({
    variables: { workspaceSlug, webappSlug },
    skip: isPublic || !!initialWebapp,
  });

  const loading = isPublic ? publicQueryResult.loading : authenticatedQueryResult.loading;

  if (isPublic && initialWebapp) {
    return (
      <Page title={initialWebapp.name}>
        <div className="h-screen flex flex-col">
          <div className="flex-1 min-h-0">
            <WebappIframe
              url={initialWebapp.url ?? undefined}
              type={initialWebapp.type}
              workspaceSlug={workspaceSlug}
              webappSlug={webappSlug}
            />
          </div>
          <div className="bg-white border-t border-gray-200 px-4 py-2 flex items-center justify-center gap-2 shadow-sm">
            <span className="text-xs text-gray-600">{t("Powered by")}</span>
            <img
              src="/images/logo_with_text_black.svg"
              alt="OpenHEXA"
              className="h-5"
            />
          </div>
        </div>
      </Page>
    );
  }

  if (!isPublic && initialWebapp && initialWorkspace) {
    return (
      <Page title={t("Web Apps")}>
        <WorkspaceLayout
          workspace={initialWorkspace}
          header={
            <Breadcrumbs withHome={false} className="flex-1">
              <Breadcrumbs.Part
                isFirst
                href={`/workspaces/${encodeURIComponent(initialWorkspace.slug)}/webapps`}
              >
                {t("Web Apps")}
              </Breadcrumbs.Part>
              <Breadcrumbs.Part
                href={`/workspaces/${encodeURIComponent(
                  initialWorkspace.slug,
                )}/webapps/${encodeURIComponent(initialWebapp.slug)}`}
                isLast
              >
                {initialWebapp.name}
              </Breadcrumbs.Part>
            </Breadcrumbs>
          }
        >
          <WorkspaceLayout.PageContent>
            <WebappIframe
              url={initialWebapp.url ?? undefined}
              type={initialWebapp.type}
              workspaceSlug={workspaceSlug}
              webappSlug={webappSlug}
            />
          </WorkspaceLayout.PageContent>
        </WorkspaceLayout>
      </Page>
    );
  }

  if (loading) {
    return null;
  }

  if (isPublic) {
    const webapp = publicQueryResult.data?.publicWebapp;
    if (!webapp) return null;

    return (
      <Page title={webapp.name}>
        <div className="h-screen flex flex-col">
          <div className="flex-1 min-h-0">
            <WebappIframe
              url={webapp.url ?? undefined}
              type={webapp.type}
              workspaceSlug={workspaceSlug}
              webappSlug={webappSlug}
            />
          </div>
          <div className="bg-white border-t border-gray-200 px-4 py-2 flex items-center justify-center gap-2 shadow-sm">
            <span className="text-xs text-gray-600">{t("Powered by")}</span>
            <img
              src="/images/logo_with_text_black.svg"
              alt="OpenHEXA"
              className="h-5"
            />
          </div>
        </div>
      </Page>
    );
  }

  const workspace = authenticatedQueryResult.data?.workspace;
  const webapp = authenticatedQueryResult.data?.webapp;

  if (!workspace || !webapp) {
    return null;
  }

  return (
    <Page title={t("Web Apps")}>
      <WorkspaceLayout
        workspace={workspace}
        forceCompactSidebar={true}
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
          <WebappIframe
            url={webapp.url ?? undefined}
            type={webapp.type}
            workspaceSlug={workspace.slug}
            webappSlug={webapp.slug}
          />
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
          isPublic: data.webapp.isPublic,
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
        webapp: data.publicWebapp,
        isPublic: true,
      },
    };
  },
});

export default WorkspaceWebappPlayPage;

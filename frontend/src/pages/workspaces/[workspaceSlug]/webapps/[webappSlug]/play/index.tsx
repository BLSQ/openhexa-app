import Page from "core/components/Page";
import { createGetServerSideProps } from "core/helpers/page";
import { NextPageWithLayout } from "core/helpers/types";
import { useTranslation } from "next-i18next";
import WorkspaceLayout from "workspaces/layouts/WorkspaceLayout";
import Breadcrumbs from "core/components/Breadcrumbs";
import WebappIframe from "webapps/features/WebappIframe";
import { WebappType } from "graphql/types";
import {
  WebappAccessDocument,
  WebappAccessQuery,
} from "webapps/graphql/queries.generated";

type Props = {
  webapp: NonNullable<WebappAccessQuery["webapp"]>;
  isAuthenticated: boolean;
};

const WorkspaceWebappPlayPage: NextPageWithLayout = (props: Props) => {
  const { webapp, isAuthenticated } = props;
  const { t } = useTranslation();

  if (!isAuthenticated) {
    return (
      <Page title={webapp.name}>
        <WebappIframe
          url={webapp.url}
          style={{ height: "100vh" }}
          showPoweredBy
        />
      </Page>
    );
  }

  const { workspace } = webapp;

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
          <WebappIframe url={webapp.url} />
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
    const isAuthenticated = !!ctx.me?.user;

    const { data } = await client.query<WebappAccessQuery>({
      query: WebappAccessDocument,
      variables: { workspaceSlug, webappSlug },
    });

    if (!data.webapp) {
      if (!isAuthenticated) {
        // It's possible the webapp exists but the user doesn't have access because it's not public, so we check authentication first
        return {
          redirect: {
            permanent: false,
            destination: `/login?next=${encodeURIComponent(ctx.resolvedUrl)}`,
          },
        };
      }
      return { notFound: true };
    }

    if (data.webapp.type === WebappType.Superset) {
      return {
        redirect: { permanent: false, destination: data.webapp.url },
      };
    }

    if (isAuthenticated) {
      await WorkspaceLayout.prefetch(ctx, client);
    }

    return {
      props: {
        isAuthenticated,
        webapp: data.webapp,
      },
    };
  },
});

export default WorkspaceWebappPlayPage;

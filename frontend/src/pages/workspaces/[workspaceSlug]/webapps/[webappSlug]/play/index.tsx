import Page from "core/components/Page";
import { createGetServerSideProps } from "core/helpers/page";
import { NextPageWithLayout } from "core/helpers/types";
import { getMe } from "identity/helpers/auth";
import WebappIframe from "webapps/features/WebappIframe";
import {
  WebappAccessDocument,
  WebappAccessQuery,
} from "webapps/graphql/queries.generated";
import { WebappType } from "graphql/types";

type Props = {
  webapp: NonNullable<WebappAccessQuery["webapp"]>;
};

const WorkspaceWebappPlayPage: NextPageWithLayout = (props: Props) => {
  const { webapp } = props;

  return (
    <Page title={webapp.name}>
      <WebappIframe
        url={webapp.url}
        type={webapp.type}
        style={{ height: "100vh" }}
        showPoweredBy={
          webapp.showPoweredBy && webapp.type !== WebappType.Superset
        } // There is already a banner in the Superset iframe from the backend
      />
    </Page>
  );
};

WorkspaceWebappPlayPage.getLayout = (page) => page;

export const getServerSideProps = createGetServerSideProps({
  requireAuth: false,
  async getServerSideProps(ctx, client) {
    const workspaceSlug = ctx.params!.workspaceSlug as string;
    const webappSlug = ctx.params!.webappSlug as string;

    const { data } = await client.query<WebappAccessQuery>({
      query: WebappAccessDocument,
      variables: { workspaceSlug, webappSlug },
    });

    if (!data.webapp) {
      const me = await getMe(ctx);
      if (!me?.user) {
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

    return {
      props: {
        webapp: data.webapp,
      },
    };
  },
});

export default WorkspaceWebappPlayPage;

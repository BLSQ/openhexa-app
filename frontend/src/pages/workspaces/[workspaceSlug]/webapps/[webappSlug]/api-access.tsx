import Page from "core/components/Page";
import { createGetServerSideProps } from "core/helpers/page";
import { NextPageWithLayout } from "core/helpers/types";
import {
  useWorkspaceWebappPageQuery,
  WorkspaceWebappPageDocument,
  WorkspaceWebappPageQuery,
  WorkspaceWebappPageQueryVariables,
} from "workspaces/graphql/queries.generated";
import WebappLayout from "workspaces/layouts/WebappLayout";
import WebappApiAccess from "webapps/features/WebappApiAccess";
import useCacheKey from "core/hooks/useCacheKey";
import { WebappType } from "graphql/types";

type Props = {
  webappSlug: string;
  workspaceSlug: string;
};

const WorkspaceWebappApiAccessPage: NextPageWithLayout = (props: Props) => {
  const { webappSlug, workspaceSlug } = props;

  const { data, refetch } = useWorkspaceWebappPageQuery({
    variables: { workspaceSlug, webappSlug },
  });
  useCacheKey("webapps", refetch);

  if (!data?.workspace || !data?.webapp) {
    return null;
  }

  const { workspace, webapp } = data;

  if (webapp.type !== WebappType.Static || webapp.isPublic) {
    return null;
  }

  return (
    <Page title={webapp.name}>
      <WebappLayout
        workspace={workspace}
        webapp={webapp}
        currentTab="api-access"
      >
        <WebappApiAccess webapp={webapp} />
      </WebappLayout>
    </Page>
  );
};

WorkspaceWebappApiAccessPage.getLayout = (page) => page;

export const getServerSideProps = createGetServerSideProps({
  requireAuth: true,
  async getServerSideProps(ctx, client) {
    await WebappLayout.prefetch(ctx, client);
    const { data } = await client.query<
      WorkspaceWebappPageQuery,
      WorkspaceWebappPageQueryVariables
    >({
      query: WorkspaceWebappPageDocument,
      variables: {
        workspaceSlug: ctx.params!.workspaceSlug as string,
        webappSlug: ctx.params!.webappSlug as string,
      },
    });

    if (!data.workspace || !data.webapp) {
      return { notFound: true };
    }

    return {
      props: {
        workspaceSlug: ctx.params!.workspaceSlug,
        webappSlug: ctx.params!.webappSlug,
      },
    };
  },
});

export default WorkspaceWebappApiAccessPage;

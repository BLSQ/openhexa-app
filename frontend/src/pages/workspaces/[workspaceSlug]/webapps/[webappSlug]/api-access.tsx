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
import { useRouter } from "next/router";
import { useEffect } from "react";

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
  const router = useRouter();
  const hasNoApiAccess =
    data?.webapp?.type !== WebappType.Static || data?.webapp?.isPublic;

  // The tab disappears once the app is made public from the header, which would
  // otherwise leave the user on a blank page.
  useEffect(() => {
    if (data?.webapp && hasNoApiAccess) {
      router.replace(
        `/workspaces/${encodeURIComponent(workspaceSlug)}/webapps/${encodeURIComponent(webappSlug)}`,
      );
    }
  }, [data?.webapp, hasNoApiAccess, router, workspaceSlug, webappSlug]);

  if (!data?.workspace || !data?.webapp) {
    return null;
  }

  const { workspace, webapp } = data;

  if (hasNoApiAccess) {
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

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
import WebappLayout from "workspaces/layouts/WebappLayout";
import WebappHistory from "webapps/features/WebappHistory/WebappHistory";
import useCacheKey from "core/hooks/useCacheKey";
import DataCard from "core/components/DataCard";
import { WebappType } from "graphql/types";

type Props = {
  webappSlug: string;
  workspaceSlug: string;
};

const WorkspaceWebappHistoryPage: NextPageWithLayout = (props: Props) => {
  const { webappSlug, workspaceSlug } = props;
  const { t } = useTranslation();

  const { data, refetch } = useWorkspaceWebappPageQuery({
    variables: { workspaceSlug, webappSlug },
  });
  useCacheKey("webapps", refetch);

  if (!data?.workspace || !data?.webapp) {
    return null;
  }

  const { workspace, webapp } = data;

  if (webapp.type !== WebappType.Static) {
    return null;
  }

  return (
    <Page title={webapp.name}>
      <WebappLayout workspace={workspace} webapp={webapp} currentTab="history">
        <DataCard.FormSection>
          <WebappHistory
            workspaceSlug={workspace.slug}
            webappSlug={webapp.slug}
          />
        </DataCard.FormSection>
      </WebappLayout>
    </Page>
  );
};

WorkspaceWebappHistoryPage.getLayout = (page) => page;

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

export default WorkspaceWebappHistoryPage;

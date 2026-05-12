import Page from "core/components/Page";
import { createGetServerSideProps } from "core/helpers/page";
import { NextPageWithLayout } from "core/helpers/types";
import { useTranslation } from "next-i18next";
import Link from "next/link";
import {
  useWorkspaceWebappPageQuery,
  WorkspaceWebappPageDocument,
  WorkspaceWebappPageQuery,
  WorkspaceWebappPageQueryVariables,
} from "workspaces/graphql/queries.generated";
import WebappLayout from "workspaces/layouts/WebappLayout";
import CommitDiff from "webapps/features/CommitDiff/CommitDiff";
import useCacheKey from "core/hooks/useCacheKey";
import DataCard from "core/components/DataCard";
import { WebappType } from "graphql/types";
type Props = {
  webappSlug: string;
  workspaceSlug: string;
  commitId: string;
};

const WorkspaceWebappCommitDiffPage: NextPageWithLayout = (props: Props) => {
  const { webappSlug, workspaceSlug, commitId } = props;
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
          <div className="mb-4">
            <Link
              href={`/workspaces/${encodeURIComponent(workspaceSlug)}/webapps/${encodeURIComponent(webappSlug)}/history`}
              className="text-sm text-gray-500 hover:text-gray-700 hover:underline"
            >
              {t("← Back to history")}
            </Link>
          </div>
          <CommitDiff
            workspaceSlug={workspace.slug}
            webappSlug={webapp.slug}
            commitId={commitId}
          />
        </DataCard.FormSection>
      </WebappLayout>
    </Page>
  );
};

WorkspaceWebappCommitDiffPage.getLayout = (page) => page;

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
        commitId: ctx.params!.commitId,
      },
    };
  },
});

export default WorkspaceWebappCommitDiffPage;

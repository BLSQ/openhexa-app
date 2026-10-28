import Breadcrumbs from "core/components/Breadcrumbs";
import Page from "core/components/Page";
import { isValidUuid } from "core/helpers";
import { createGetServerSideProps } from "core/helpers/page";
import { NextPageWithLayout } from "core/helpers/types";
import { useTranslation } from "next-i18next";
import SavedQueryDetail from "workspaces/features/SavedQueryDetail";
import {
  useWorkspaceSavedQueryPageQuery,
  WorkspaceSavedQueryPageDocument,
  WorkspaceSavedQueryPageQuery,
  WorkspaceSavedQueryPageQueryVariables,
  WorkspaceSavedQuerySlugByIdDocument,
  WorkspaceSavedQuerySlugByIdQuery,
  WorkspaceSavedQuerySlugByIdQueryVariables,
} from "workspaces/graphql/queries.generated";
import { dataStudioRoutes } from "workspaces/helpers/dataStudio";
import DataStudioLayout from "workspaces/layouts/DataStudioLayout";
import WorkspaceLayout from "workspaces/layouts/WorkspaceLayout";

type Props = {
  workspaceSlug: string;
  querySlug: string;
};

const WorkspaceSavedQueryPage: NextPageWithLayout = (props: Props) => {
  const { t } = useTranslation();
  const { data, refetch } = useWorkspaceSavedQueryPageQuery({
    variables: { workspaceSlug: props.workspaceSlug, slug: props.querySlug },
  });

  if (!data?.workspace) {
    return null;
  }
  const { workspace, savedQueryBySlug: savedQuery } = data;
  const routes = dataStudioRoutes(workspace.slug);

  return (
    <Page title={savedQuery?.name || t("Data Studio")}>
      <WorkspaceLayout
        workspace={workspace}
        withMarginBottom={false}
        className="h-screen"
        header={
          <Breadcrumbs withHome={false} className="flex-1">
            <Breadcrumbs.Part isFirst href={routes.base}>
              {t("Data Studio")}
            </Breadcrumbs.Part>
            <Breadcrumbs.Part href={routes.queries}>
              {t("Saved queries")}
            </Breadcrumbs.Part>
            {savedQuery && (
              <Breadcrumbs.Part isLast href={routes.query(savedQuery.slug)}>
                {savedQuery.name}
              </Breadcrumbs.Part>
            )}
          </Breadcrumbs>
        }
      >
        {savedQuery ? (
          // key: remount the page body when switching between saved queries so
          // the editor re-initialises from the newly loaded content.
          <div key={savedQuery.id} className="h-full min-h-0">
            <SavedQueryDetail
              workspaceSlug={workspace.slug}
              savedQuery={savedQuery}
              canCreate={workspace.permissions.createSavedQuery}
              showAssistant={
                workspace.organization?.aiSettings?.enabled ?? false
              }
              aiBudgetLimitReached={
                workspace.organization?.aiBudgetLimitReached ?? false
              }
              onRefetch={() => {
                refetch().then();
              }}
            />
          </div>
        ) : (
          // Defensive fallback: normally SSR returns notFound (404) when the
          // query is missing, so this only renders if the workspace resolves
          // but the saved query is absent from the client cache.
          <div className="flex h-full flex-col items-center justify-center gap-1 p-8 text-center">
            <p className="text-sm font-medium text-gray-800">
              {t("Saved query not found")}
            </p>
            <p className="text-sm text-gray-500">
              {t("It may have been deleted.")}
            </p>
          </div>
        )}
      </WorkspaceLayout>
    </Page>
  );
};

WorkspaceSavedQueryPage.getLayout = (page) => page;

export const getServerSideProps = createGetServerSideProps({
  requireAuth: true,
  async getServerSideProps(ctx, client) {
    await DataStudioLayout.prefetch(ctx, client);
    const workspaceSlug = ctx.params?.workspaceSlug as string;
    const querySlug = ctx.params?.querySlug as string;

    const { data } = await client.query<
      WorkspaceSavedQueryPageQuery,
      WorkspaceSavedQueryPageQueryVariables
    >({
      query: WorkspaceSavedQueryPageDocument,
      variables: { workspaceSlug, slug: querySlug },
    });

    if (!data.workspace) {
      return { notFound: true };
    }

    if (!data.savedQueryBySlug) {
      // Saved queries used to be addressed by id. A link made before the move
      // still resolves, once: redirect it to the slug URL rather than 404.
      if (isValidUuid(querySlug)) {
        const { data: byId } = await client.query<
          WorkspaceSavedQuerySlugByIdQuery,
          WorkspaceSavedQuerySlugByIdQueryVariables
        >({
          query: WorkspaceSavedQuerySlugByIdDocument,
          variables: { workspaceSlug, id: querySlug },
        });
        if (byId.savedQuery) {
          return {
            redirect: {
              destination: dataStudioRoutes(workspaceSlug).query(
                byId.savedQuery.slug,
              ),
              permanent: false,
            },
          };
        }
      }
      return { notFound: true };
    }

    return {
      props: {
        workspaceSlug: data.workspace.slug,
        querySlug,
      },
    };
  },
});

export default WorkspaceSavedQueryPage;

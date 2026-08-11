import Page from "core/components/Page";
import { createGetServerSideProps } from "core/helpers/page";
import { NextPageWithLayout } from "core/helpers/types";
import { useTranslation } from "next-i18next";
import DataStudioEditor from "workspaces/features/DataStudioEditor";
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

type Props = {
  workspaceSlug: string;
  querySlug: string;
};

const UUID_RE =
  /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;

const WorkspaceSavedQueryPage: NextPageWithLayout = (props: Props) => {
  const { t } = useTranslation();
  const { data } = useWorkspaceSavedQueryPageQuery({
    variables: { workspaceSlug: props.workspaceSlug, slug: props.querySlug },
  });

  if (!data?.workspace) {
    return null;
  }
  const { workspace, savedQueryBySlug: savedQuery } = data;

  return (
    <Page title={savedQuery?.name || t("Data Studio")}>
      <DataStudioLayout workspace={workspace} currentTab="editor">
        {savedQuery ? (
          // key: remount the editor when switching between saved queries so it
          // re-initialises from the newly loaded content.
          <div className="h-full p-4">
            <DataStudioEditor
              key={savedQuery.id}
              workspaceSlug={workspace.slug}
              savedQuery={savedQuery}
              canCreate={workspace.permissions.createSavedQuery}
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
      </DataStudioLayout>
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
      if (UUID_RE.test(querySlug)) {
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

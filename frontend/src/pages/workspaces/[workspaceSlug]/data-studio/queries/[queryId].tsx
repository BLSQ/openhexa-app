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
} from "workspaces/graphql/queries.generated";
import DataStudioLayout from "workspaces/layouts/DataStudioLayout";

type Props = {
  workspaceSlug: string;
  queryId: string;
};

const WorkspaceSavedQueryPage: NextPageWithLayout = (props: Props) => {
  const { t } = useTranslation();
  const { data } = useWorkspaceSavedQueryPageQuery({
    variables: { workspaceSlug: props.workspaceSlug, id: props.queryId },
  });

  if (!data?.workspace || !data.savedQuery) {
    return null;
  }
  const { workspace, savedQuery } = data;

  return (
    <Page title={savedQuery.name || t("Data Studio")}>
      <DataStudioLayout workspace={workspace} currentTab="editor">
        {/* key: remount the editor when switching between saved queries so it
            re-initialises from the newly loaded content. */}
        <div className="h-full p-4">
          <DataStudioEditor
            key={savedQuery.id}
            workspaceSlug={workspace.slug}
            savedQuery={savedQuery}
            canCreate={workspace.permissions.createSavedQuery}
          />
        </div>
      </DataStudioLayout>
    </Page>
  );
};

WorkspaceSavedQueryPage.getLayout = (page) => page;

export const getServerSideProps = createGetServerSideProps({
  requireAuth: true,
  async getServerSideProps(ctx, client) {
    await DataStudioLayout.prefetch(ctx, client);
    const { data } = await client.query<
      WorkspaceSavedQueryPageQuery,
      WorkspaceSavedQueryPageQueryVariables
    >({
      query: WorkspaceSavedQueryPageDocument,
      variables: {
        workspaceSlug: ctx.params?.workspaceSlug as string,
        id: ctx.params?.queryId as string,
      },
    });

    if (!data.workspace || !data.savedQuery) {
      return {
        notFound: true,
      };
    }
    return {
      props: {
        workspaceSlug: data.workspace.slug,
        queryId: ctx.params?.queryId as string,
      },
    };
  },
});

export default WorkspaceSavedQueryPage;

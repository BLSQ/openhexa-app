import Page from "core/components/Page";
import { createGetServerSideProps } from "core/helpers/page";
import { NextPageWithLayout } from "core/helpers/types";
import { useTranslation } from "next-i18next";
import DataStudioEditor from "workspaces/features/DataStudioEditor";
import {
  useWorkspaceDataStudioPageQuery,
  WorkspaceDataStudioPageDocument,
} from "workspaces/graphql/queries.generated";
import DataStudioLayout from "workspaces/layouts/DataStudioLayout";

type Props = {
  workspaceSlug: string;
};

const WorkspaceDataStudioPage: NextPageWithLayout = (props: Props) => {
  const { t } = useTranslation();
  const { data } = useWorkspaceDataStudioPageQuery({
    variables: { workspaceSlug: props.workspaceSlug },
  });

  if (!data?.workspace) {
    return null;
  }
  const { workspace } = data;

  return (
    <Page title={t("Data Studio")}>
      <DataStudioLayout workspace={workspace} currentTab="editor">
        {/* Full-bleed IDE: fill the area below the header and sub-nav. */}
        <div className="h-full p-4">
          <DataStudioEditor
            workspaceSlug={workspace.slug}
            canCreate={workspace.permissions.createSavedQuery}
          />
        </div>
      </DataStudioLayout>
    </Page>
  );
};

WorkspaceDataStudioPage.getLayout = (page) => page;

export const getServerSideProps = createGetServerSideProps({
  requireAuth: true,
  async getServerSideProps(ctx, client) {
    await DataStudioLayout.prefetch(ctx, client);
    const { data } = await client.query({
      query: WorkspaceDataStudioPageDocument,
      variables: {
        workspaceSlug: ctx.params?.workspaceSlug,
      },
    });

    if (!data.workspace) {
      return {
        notFound: true,
      };
    }
    return {
      props: { workspaceSlug: data.workspace.slug },
    };
  },
});

export default WorkspaceDataStudioPage;

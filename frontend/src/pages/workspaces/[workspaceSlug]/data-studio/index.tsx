import Breadcrumbs from "core/components/Breadcrumbs";
import Page from "core/components/Page";
import { createGetServerSideProps } from "core/helpers/page";
import { NextPageWithLayout } from "core/helpers/types";
import { useTranslation } from "next-i18next";
import DataStudioEditor from "workspaces/features/DataStudioEditor";
import {
  useWorkspaceDataStudioPageQuery,
  WorkspaceDataStudioPageDocument,
} from "workspaces/graphql/queries.generated";
import WorkspaceLayout from "workspaces/layouts/WorkspaceLayout";

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
      <WorkspaceLayout
        workspace={workspace}
        withMarginBottom={false}
        header={
          <Breadcrumbs withHome={false}>
            <Breadcrumbs.Part
              isFirst
              isLast
              href={`/workspaces/${encodeURIComponent(
                workspace.slug,
              )}/data-studio`}
            >
              {t("Data Studio")}
            </Breadcrumbs.Part>
          </Breadcrumbs>
        }
      >
        {/* Full-bleed IDE: fill the viewport below the fixed 4rem workspace header. */}
        <div className="h-[calc(100vh-4rem)] p-4">
          <DataStudioEditor workspaceSlug={workspace.slug} />
        </div>
      </WorkspaceLayout>
    </Page>
  );
};

WorkspaceDataStudioPage.getLayout = (page) => page;

export const getServerSideProps = createGetServerSideProps({
  requireAuth: true,
  async getServerSideProps(ctx, client) {
    await WorkspaceLayout.prefetch(ctx, client);
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

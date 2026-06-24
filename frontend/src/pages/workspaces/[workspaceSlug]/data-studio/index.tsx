import Breadcrumbs from "core/components/Breadcrumbs";
import Page from "core/components/Page";
import { createGetServerSideProps } from "core/helpers/page";
import { NextPageWithLayout } from "core/helpers/types";
import { useTranslation } from "next-i18next";
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
        <WorkspaceLayout.PageContent>
          <p className="text-gray-500">{t("Data Studio")}</p>
        </WorkspaceLayout.PageContent>
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

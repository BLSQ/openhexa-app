import Page from "core/components/Page";
import { createGetServerSideProps } from "core/helpers/page";
import useFeature from "identity/hooks/useFeature";
import useMe from "identity/hooks/useMe";
import { useRouter } from "next/router";
import { ReactElement } from "react";
import { useTranslation } from "react-i18next";
import CreateWorkspaceDialog from "workspaces/features/CreateWorkspaceDialog";
import {
  WorkspacesPageDocument,
  WorkspacesPageQuery,
} from "workspaces/graphql/queries.generated";

const WorkspacesHome = () => {
  const router = useRouter();
  const [hasWorkspacesEnabled] = useFeature("workspaces");
  const me = useMe();
  const { t } = useTranslation();

  const handleClose = () => {};

  if (hasWorkspacesEnabled && me.permissions.createWorkspace) {
    return (
      <Page title={t("New workspace")}>
        <CreateWorkspaceDialog open onClose={handleClose} />
      </Page>
    );
  } else {
    router.push("/dashboard");
  }
};

WorkspacesHome.getLayout = (page: ReactElement) => page;

export const getServerSideProps = createGetServerSideProps({
  requireAuth: true,
  async getServerSideProps(ctx, client) {
    const { data } = await client.query<WorkspacesPageQuery>({
      query: WorkspacesPageDocument,
      variables: {},
    });

    if (!data.workspaces || !data.workspaces.items.length) {
      return {
        props: {},
      };
    }

    const latestWorkspace = data.workspaces.items[0];
    return {
      redirect: {
        permanent: false,
        destination: `/workspaces/${latestWorkspace.id}`,
      },
    };
  },
});
export default WorkspacesHome;

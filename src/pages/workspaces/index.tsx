import Alert from "core/components/Alert";
import Page from "core/components/Page";
import { createGetServerSideProps } from "core/helpers/page";
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
  const { t } = useTranslation();
  const me = useMe();
  const router = useRouter();
  const handleClose = () => {};

  if (!me.permissions.createWorkspace) {
    return (
      <Alert onClose={() => router.push("/")} icon="warning">
        {t("No workspace available at the moment")}
      </Alert>
    );
  }

  return (
    <Page title={t("New workspace")}>
      <CreateWorkspaceDialog open onClose={handleClose} />
    </Page>
  );
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
      if (ctx.me?.features.filter((f) => f.code === "workspaces")[0]) {
        return {
          props: {},
        };
      }
      return {
        redirect: {
          permanent: false,
          destination: `/`,
        },
      };
    }

    const latestWorkspace = data.workspaces.items[0];
    return {
      redirect: {
        permanent: false,
        destination: `/workspaces/${latestWorkspace.slug}`,
      },
    };
  },
});
export default WorkspacesHome;

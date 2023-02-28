import Alert from "core/components/Alert";
import Page from "core/components/Page";
import { createGetServerSideProps } from "core/helpers/page";
import { NextPageWithLayout } from "core/helpers/types";
import { useTranslation } from "next-i18next";
import { useRouter } from "next/router";
import { LaunchNotebookServerDocument } from "workspaces/graphql/mutations.generated";
import {
  WorkspacePageDocument,
  WorkspacePageQuery,
} from "workspaces/graphql/queries.generated";
import WorkspaceLayout from "workspaces/layouts/WorkspaceLayout";

type Props = {
  notebooksUrl: string;
};

const WorkspaceNotebooksPage: NextPageWithLayout = (props: Props) => {
  const { t } = useTranslation();
  const router = useRouter();
  const workspaceSlug = router.query.workspaceSlug as string;
  if (!props.notebooksUrl) {
    return (
      <Alert
        onClose={() => {
          router.push({
            pathname: "/workspaces/[workspaceSlug]",
            query: { workspaceSlug: workspaceSlug },
          });
        }}
        icon="error"
      >
        {t("Unable to start JupytherHub for this workspace.")}
      </Alert>
    );
  }

  return (
    <Page title={t("Workspace")}>
      <iframe
        className="h-full w-full flex-1"
        src={props.notebooksUrl}
      ></iframe>
    </Page>
  );
};

WorkspaceNotebooksPage.getLayout = (page, pageProps) => {
  return (
    <WorkspaceLayout mainClassName="min-h-screen" pageProps={pageProps}>
      {page}
    </WorkspaceLayout>
  );
};

export const getServerSideProps = createGetServerSideProps({
  requireAuth: true,
  getServerSideProps: async (ctx, client) => {
    const { data } = await client.query<WorkspacePageQuery>({
      query: WorkspacePageDocument,
      variables: {
        slug: ctx.params?.workspaceSlug,
      },
    });

    if (!data.workspace) {
      return {
        notFound: true,
      };
    }
    const response = await client.mutate({
      mutation: LaunchNotebookServerDocument,
      variables: { input: { workspaceSlug: ctx.params?.workspaceSlug } },
    });

    if (!response.data?.launchNotebookServer.success) {
      return {
        props: {},
      };
    }
    const { launchNotebookServer } = response.data;
    return {
      props: {
        notebooksUrl: launchNotebookServer.server.url,
      },
    };
  },
});

export default WorkspaceNotebooksPage;

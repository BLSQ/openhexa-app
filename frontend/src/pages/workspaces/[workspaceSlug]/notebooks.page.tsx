import { useApolloClient } from "@apollo/client";
import Breadcrumbs from "core/components/Breadcrumbs";
import Page from "core/components/Page";
import Spinner from "core/components/Spinner";
import { createGetServerSideProps } from "core/helpers/page";
import { NextPageWithLayout } from "core/helpers/types";
import { NotebookServer } from "graphql/types";
import { useTranslation } from "next-i18next";
import { useRouter } from "next/router";
import { useEffect, useState } from "react";
import {
  useWorkspaceNotebooksPageQuery,
  WorkspaceNotebooksPageDocument,
  WorkspaceNotebooksPageQuery,
} from "workspaces/graphql/queries.generated";
import { launchNotebookServer } from "workspaces/helpers/notebooks";
import WorkspaceLayout from "workspaces/layouts/WorkspaceLayout";
import { ErrorAlert } from "core/components/Alert";

type Props = {
  server: NotebookServer;
};

const WorkspaceNotebooksPage: NextPageWithLayout = (props: Props) => {
  const { t } = useTranslation();
  const router = useRouter();
  const client = useApolloClient();
  const [server, setServer] = useState(props.server);
  const workspaceSlug = router.query.workspaceSlug as string;
  const { data } = useWorkspaceNotebooksPageQuery({
    variables: { workspaceSlug },
  });

  useEffect(() => {
    let timeout: NodeJS.Timeout;
    if (!server?.ready) {
      timeout = setTimeout(() => {
        launchNotebookServer(client, workspaceSlug).then(setServer);
      }, 1000);
    }
    return () => clearTimeout(timeout);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [server]);

  if (!data?.workspace) {
    return null;
  }

  if (!server) {
    return (
      <ErrorAlert
        onClose={() => {
          router.push({
            pathname: "/workspaces/[workspaceSlug]",
            query: { workspaceSlug: workspaceSlug },
          });
        }}
      >
        {t("Unable to start JupytherHub for this workspace.")}
      </ErrorAlert>
    );
  }

  return (
    <Page title={data.workspace.name}>
      <WorkspaceLayout
        workspace={data.workspace}
        helpLinks={[
          {
            label: t("Using notebooks in OpenHEXA"),
            href: "https://github.com/BLSQ/openhexa/wiki/Using-notebooks-in-OpenHEXA",
          },
        ]}
        forceCompactSidebar
        withMarginBottom={false}
        header={
          <Breadcrumbs withHome={false}>
            <Breadcrumbs.Part
              isFirst
              href={`/workspaces/${encodeURIComponent(data.workspace.slug)}`}
            >
              {data.workspace.name}
            </Breadcrumbs.Part>
            <Breadcrumbs.Part
              href={`/workspaces/${encodeURIComponent(
                data.workspace.slug,
              )}/notebooks`}
              isLast
            >
              {t("Notebooks")}
            </Breadcrumbs.Part>
          </Breadcrumbs>
        }
      >
        {server?.ready ? (
          <iframe
            width="100%"
            style={{ height: "calc(100vh - 4rem)" }}
            src={server.url}
          ></iframe>
        ) : (
          <div className="flex h-60 flex-1 flex-col items-center justify-center gap-4">
            <Spinner size="lg" />
            <div className="text-gray-500">
              {t("Starting your Jupyter server...")}
            </div>
          </div>
        )}
      </WorkspaceLayout>
    </Page>
  );
};

WorkspaceNotebooksPage.getLayout = (page) => page;

export const getServerSideProps = createGetServerSideProps({
  requireAuth: true,
  getServerSideProps: async (ctx, client) => {
    await WorkspaceLayout.prefetch(ctx, client);
    const { data } = await client.query<WorkspaceNotebooksPageQuery>({
      query: WorkspaceNotebooksPageDocument,
      variables: { workspaceSlug: ctx.params?.workspaceSlug },
    });

    if (!data.workspace || !data.workspace.permissions.launchNotebookServer) {
      return {
        notFound: true,
      };
    }
    const server = await launchNotebookServer(
      client,
      ctx.params?.workspaceSlug as string,
    );

    return {
      props: {
        server,
      },
    };
  },
});

export default WorkspaceNotebooksPage;

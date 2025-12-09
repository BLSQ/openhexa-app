import Page from "core/components/Page";
import { createGetServerSideProps } from "core/helpers/page";
import { NextPageWithLayout } from "core/helpers/types";
import { useTranslation } from "next-i18next";
import {
  useWorkspaceWebappPageQuery,
  WorkspaceWebappPageDocument,
  WorkspaceWebappPageQuery,
  WorkspaceWebappPageQueryVariables,
} from "workspaces/graphql/queries.generated";
import WorkspaceLayout from "workspaces/layouts/WorkspaceLayout";
import Breadcrumbs from "core/components/Breadcrumbs";
import WebappForm from "webapps/features/WebappForm";
import { TrashIcon } from "@heroicons/react/24/outline";
import Button from "core/components/Button";
import { useState } from "react";
import DeleteWebappDialog from "workspaces/features/DeleteWebappDialog/DeleteWebappDialog";
import useCacheKey from "core/hooks/useCacheKey";

type Props = {
  webappSlug: string;
  workspaceSlug: string;
};

const WorkspaceWebappPage: NextPageWithLayout = (props: Props) => {
  const { webappSlug, workspaceSlug } = props;
  const { t } = useTranslation();
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false);

  const { data, refetch } = useWorkspaceWebappPageQuery({
    variables: {
      workspaceSlug,
      webappSlug,
    },
  });
  useCacheKey("webapps", refetch);

  if (!data?.workspace || !data?.webapp) {
    return null;
  }

  const { workspace, webapp } = data;

  return (
    <Page title={t("Web Apps")}>
      <WorkspaceLayout
        workspace={workspace}
        header={
          <Breadcrumbs withHome={false} className="flex-1">
            <Breadcrumbs.Part
              isFirst
              href={`/workspaces/${encodeURIComponent(workspace.slug)}`}
            >
              {workspace.name}
            </Breadcrumbs.Part>
            <Breadcrumbs.Part
              href={`/workspaces/${encodeURIComponent(
                workspace.slug,
              )}/webapps`}
            >
              {t("Web Apps")}
            </Breadcrumbs.Part>
            <Breadcrumbs.Part
              href={`/workspaces/${encodeURIComponent(
                workspace.slug,
              )}/webapps/${encodeURIComponent(webapp.slug)}`}
              isLast
            >
              {webapp.name}
            </Breadcrumbs.Part>
          </Breadcrumbs>
        }
        headerActions={
          webapp?.permissions.delete && (
            <Button
              variant={"danger"}
              leadingIcon={<TrashIcon className="h-4 w-4" />}
              onClick={() => setIsDeleteDialogOpen(true)}
            >
              {t("Delete")}
            </Button>
          )
        }
      >
        <WorkspaceLayout.PageContent>
          <WebappForm workspace={workspace} webapp={webapp} />
        </WorkspaceLayout.PageContent>
      </WorkspaceLayout>
      <DeleteWebappDialog
        open={isDeleteDialogOpen}
        onClose={() => setIsDeleteDialogOpen(false)}
        webapp={webapp}
        workspace={workspace}
      />
    </Page>
  );
};

WorkspaceWebappPage.getLayout = (page) => page;

export const getServerSideProps = createGetServerSideProps({
  requireAuth: true,
  async getServerSideProps(ctx, client) {
    await WorkspaceLayout.prefetch(ctx, client);
    const { data } = await client.query<
      WorkspaceWebappPageQuery,
      WorkspaceWebappPageQueryVariables
    >({
      query: WorkspaceWebappPageDocument,
      variables: {
        workspaceSlug: ctx.params!.workspaceSlug as string,
        webappSlug: ctx.params!.webappSlug as string,
      },
    });

    if (!data.workspace || !data.webapp) {
      return { notFound: true };
    }

    return {
      props: {
        workspaceSlug: ctx.params!.workspaceSlug,
        webappSlug: ctx.params!.webappSlug,
        workspace: data.workspace,
        webapp: data.webapp,
      },
    };
  },
});

export default WorkspaceWebappPage;

import { EyeIcon } from "@heroicons/react/24/outline";
import Breadcrumbs from "core/components/Breadcrumbs";
import Button from "core/components/Button";
import Page from "core/components/Page";
import { createGetServerSideProps } from "core/helpers/page";
import { NextPageWithLayout } from "core/helpers/types";
import useCacheKey from "core/hooks/useCacheKey";
import { WebappType } from "graphql/types";
import { useTranslation } from "next-i18next";
import Link from "next/link";
import { useState } from "react";
import WebappDetail from "webapps/features/WebappDetail/WebappDetail";
import GitClonePopover from "webapps/features/GitClonePopover/GitClonePopover";
import WebappVisibilityButton from "webapps/features/WebappVisibilityButton";
import DeleteWebappDialog from "workspaces/features/DeleteWebappDialog/DeleteWebappDialog";
import {
  useWorkspaceWebappPageQuery,
  WorkspaceWebappPageDocument,
  WorkspaceWebappPageQuery,
  WorkspaceWebappPageQueryVariables,
} from "workspaces/graphql/queries.generated";
import WebappLayout from "workspaces/layouts/WebappLayout";
import WorkspaceLayout from "workspaces/layouts/WorkspaceLayout";

type Props = {
  webappSlug: string;
  workspaceSlug: string;
};

const WorkspaceWebappPage: NextPageWithLayout = (props: Props) => {
  const { webappSlug, workspaceSlug } = props;
  const { t } = useTranslation();
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false);
  const { data, refetch } = useWorkspaceWebappPageQuery({
    variables: { workspaceSlug, webappSlug },
  });
  useCacheKey("webapps", refetch);

  if (!data?.workspace || !data?.webapp) {
    return null;
  }

  const { workspace, webapp } = data;
  const source = webapp.source;
  const repositoryUrl =
    source?.__typename === "GitSource" ? source.repositoryUrl : null;
  const showAssistant = workspace.organization?.aiSettings?.enabled ?? false;

  return (
    <Page title={webapp.name}>
      <WorkspaceLayout
        workspace={workspace}
        withMarginBottom={false}
        className="h-screen"
        header={
          <Breadcrumbs withHome={false} className="flex-1">
            <Breadcrumbs.Part
              isFirst
              href={`/workspaces/${encodeURIComponent(workspace.slug)}/webapps`}
            >
              {t("Web Apps")}
            </Breadcrumbs.Part>
            <Breadcrumbs.Part
              isLast
              href={`/workspaces/${encodeURIComponent(workspace.slug)}/webapps/${encodeURIComponent(webapp.slug)}`}
            >
              {webapp.name}
            </Breadcrumbs.Part>
          </Breadcrumbs>
        }
        headerActions={
          <div className="flex items-center gap-2">
            {repositoryUrl && webapp.type === WebappType.Static && (
              <GitClonePopover repositoryUrl={repositoryUrl} />
            )}
            <WebappVisibilityButton webapp={webapp} />
            <Link href={webapp.serveUrl ?? webapp.url ?? "#"} target="_blank">
              <Button
                variant="primary"
                leadingIcon={<EyeIcon className="h-4 w-4" />}
              >
                {t("View")}
              </Button>
            </Link>
          </div>
        }
      >
        <div className="h-full min-h-0">
          <WebappDetail
            workspaceSlug={workspaceSlug}
            webappSlug={webappSlug}
            webapp={webapp}
            showAssistant={showAssistant}
            onRefetch={() => {
              refetch().then();
            }}
            onDelete={
              webapp.permissions.delete
                ? () => setIsDeleteDialogOpen(true)
                : undefined
            }
          />
        </div>
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
    await WebappLayout.prefetch(ctx, client);
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

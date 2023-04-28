import { PlusIcon } from "@heroicons/react/24/outline";
import { constants } from "buffer";
import Breadcrumbs from "core/components/Breadcrumbs";
import Button from "core/components/Button";
import Page from "core/components/Page";
import Pagination from "core/components/Pagination";
import { createGetServerSideProps } from "core/helpers/page";
import { NextPageWithLayout } from "core/helpers/types";
import { useTranslation } from "next-i18next";
import PipelineCard from "workspaces/features/PipelineCard";
import {
  useWorkspacePipelinesPageQuery,
  WorkspacePipelinesPageDocument,
  WorkspacePipelinesPageQuery,
  WorkspacePipelinesPageQueryVariables,
} from "workspaces/graphql/queries.generated";
import { useRouter } from "next/router";
import WorkspaceLayout from "workspaces/layouts/WorkspaceLayout";
import { useState } from "react";
import CreatePipelineDialog from "workspaces/features/CreatePipelineDialog/CreatePipelineDialog";

type Props = {
  page: number;
  perPage: number;
  workspaceSlug: string;
};

const WorkspacePipelinesPage: NextPageWithLayout = (props: Props) => {
  const { t } = useTranslation();
  const { page, perPage, workspaceSlug } = props;
  const [isDialogOpen, setDialogOpen] = useState(false);
  const router = useRouter();
  const { data } = useWorkspacePipelinesPageQuery({
    variables: {
      workspaceSlug,
      page,
      perPage,
    },
  });

  if (!data?.workspace) {
    return null;
  }

  const { workspace, pipelines } = data;

  return (
    <Page title={t("Workspace")}>
      <WorkspaceLayout workspace={workspace}>
        <WorkspaceLayout.Header className="flex items-center gap-2">
          <Breadcrumbs withHome={false} className="flex-1">
            <Breadcrumbs.Part
              isFirst
              href={`/workspaces/${encodeURIComponent(workspace.slug)}`}
            >
              {workspace.name}
            </Breadcrumbs.Part>
            <Breadcrumbs.Part
              isLast
              href={`/workspaces/${encodeURIComponent(
                workspace.slug
              )}/pipelines`}
            >
              {t("Pipelines")}
            </Breadcrumbs.Part>
          </Breadcrumbs>
          <Button
            leadingIcon={<PlusIcon className="h-4 w-4" />}
            onClick={() => setDialogOpen(true)}
          >
            {t("Create")}
          </Button>
        </WorkspaceLayout.Header>
        <WorkspaceLayout.PageContent className="divide divide-y-2">
          <div className="mb-3 grid grid-cols-2 gap-4 xl:grid-cols-3 xl:gap-5">
            {pipelines.items.map((pipeline, index) => (
              <PipelineCard
                workspace={workspace}
                key={index}
                pipeline={pipeline}
              />
            ))}
          </div>
          <Pagination
            onChange={(page, perPage) =>
              router.push({
                pathname: "/workspaces/[workspaceSlug]/pipelines",
                query: {
                  page,
                  perPage,
                  workspaceSlug,
                },
              })
            }
            page={page}
            perPage={perPage}
            totalItems={pipelines.totalItems}
            countItems={pipelines.items.length}
          />
        </WorkspaceLayout.PageContent>
      </WorkspaceLayout>
      <CreatePipelineDialog
        workspace={workspace}
        open={isDialogOpen}
        onClose={() => setDialogOpen(false)}
      />
    </Page>
  );
};

WorkspacePipelinesPage.getLayout = (page) => page;

export const getServerSideProps = createGetServerSideProps({
  requireAuth: true,
  async getServerSideProps(ctx, client) {
    const { workspaceSlug } = ctx.params!;
    const page = parseInt((ctx.query.page as string) ?? "1", 10);
    const perPage = parseInt((ctx.query.perPage as string) ?? "15", 10);

    await WorkspaceLayout.prefetch(ctx, client);
    const { data } = await client.query<
      WorkspacePipelinesPageQuery,
      WorkspacePipelinesPageQueryVariables
    >({
      query: WorkspacePipelinesPageDocument,
      variables: {
        workspaceSlug: workspaceSlug as string,
        page,
        perPage,
      },
    });
    if (!data.workspace) {
      return { notFound: true };
    }
    return {
      props: {
        workspaceSlug,
        page,
        perPage,
      },
    };
  },
});

export default WorkspacePipelinesPage;

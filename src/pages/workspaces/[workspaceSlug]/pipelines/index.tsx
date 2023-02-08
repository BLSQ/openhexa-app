import { PlusIcon } from "@heroicons/react/24/outline";
import Breadcrumbs from "core/components/Breadcrumbs";
import Button from "core/components/Button";
import Page from "core/components/Page";
import { createGetServerSideProps } from "core/helpers/page";
import { NextPageWithLayout } from "core/helpers/types";
import { useTranslation } from "next-i18next";
import { useRouter } from "next/router";
import PipelineCard from "workspaces/features/PipelineCard";
import {
  useWorkspacePipelinesPageQuery,
  WorkspacePipelinesPageDocument,
} from "workspaces/graphql/queries.generated";
import { FAKE_WORKSPACE } from "workspaces/helpers/fixtures";
import WorkspaceLayout from "workspaces/layouts/WorkspaceLayout";

const WorkspacePipelinesPage: NextPageWithLayout = (props) => {
  const { t } = useTranslation();
  const router = useRouter();
  const { data } = useWorkspacePipelinesPageQuery({
    variables: { workspaceSlug: router.query.workspaceSlug as string },
  });

  if (!data?.workspace) {
    return null;
  }

  const { workspace } = data;

  return (
    <Page title={t("Workspace")}>
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
            href={`/workspaces/${encodeURIComponent(workspace.slug)}/pipelines`}
          >
            {t("Pipelines")}
          </Breadcrumbs.Part>
        </Breadcrumbs>
        <Button leadingIcon={<PlusIcon className="h-4 w-4" />}>
          {t("Create")}
        </Button>
      </WorkspaceLayout.Header>
      <WorkspaceLayout.PageContent>
        <div className="grid grid-cols-2 gap-4 xl:grid-cols-3 xl:gap-5">
          {FAKE_WORKSPACE.dags.map((dag, index) => (
            <PipelineCard
              workspaceSlug={workspace.slug}
              key={index}
              dag={dag}
            />
          ))}
        </div>
      </WorkspaceLayout.PageContent>
    </Page>
  );
};

WorkspacePipelinesPage.getLayout = (page, pageProps) => {
  return <WorkspaceLayout pageProps={pageProps}>{page}</WorkspaceLayout>;
};

export const getServerSideProps = createGetServerSideProps({
  requireAuth: true,
  async getServerSideProps(ctx, client) {
    const { data } = await client.query({
      query: WorkspacePipelinesPageDocument,
      variables: { workspaceSlug: ctx.params?.workspaceSlug },
    });

    if (!data.workspace) {
      return {
        notFound: true,
      };
    }
  },
});

export default WorkspacePipelinesPage;

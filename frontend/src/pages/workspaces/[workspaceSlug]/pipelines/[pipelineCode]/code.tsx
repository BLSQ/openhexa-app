import Page from "core/components/Page";
import { createGetServerSideProps } from "core/helpers/page";
import { NextPageWithLayout } from "core/helpers/types";
import { useTranslation } from "next-i18next";
import PipelineCodeViewer from "workspaces/features/PipelineCodeViewer";
import {
  useWorkspacePipelineCodePageQuery,
  WorkspacePipelineCodePageDocument,
  WorkspacePipelineCodePageQuery,
  WorkspacePipelineCodePageQueryVariables,
} from "workspaces/graphql/queries.generated";
import PipelineLayout from "workspaces/layouts/PipelineLayout";

type Props = {
  pipelineCode: string;
  workspaceSlug: string;
};

// TODO : fix landing page
// TODO : fix code viewer
// TODO : SDK autocomplete

const WorkspacePipelineCodePage: NextPageWithLayout = (props: Props) => {
  const { pipelineCode, workspaceSlug } = props;
  const { t } = useTranslation();

  const { data, loading, error } = useWorkspacePipelineCodePageQuery({
    variables: {
      workspaceSlug,
      pipelineCode,
    },
  });

  if (loading) {
    return (
      <Page title={t("Pipeline Code")}>
        <div className="flex items-center justify-center h-64">
          <div className="text-gray-500">{t("Loading pipeline code...")}</div>
        </div>
      </Page>
    );
  }

  if (error || !data?.workspace || !data?.pipeline) {
    return (
      <Page title={t("Pipeline Code")}>
        <div className="flex items-center justify-center h-64">
          <div className="text-red-500">
            {error ? error.message : t("Pipeline not found")}
          </div>
        </div>
      </Page>
    );
  }

  const { workspace, pipeline } = data;

  if (!pipeline.currentVersion) {
    return (
      <Page title={pipeline.name ?? t("Pipeline Code")}>
        <PipelineLayout
          workspace={workspace}
          pipeline={pipeline}
          currentTab="code"
        >
          <div className="flex items-center justify-center h-64">
            <div className="text-center">
              <div className="text-gray-500 text-lg mb-2">
                {t("No version available")}
              </div>
              <div className="text-gray-400 text-sm">
                {t("This pipeline doesn't have any versions yet.")}
              </div>
            </div>
          </div>
        </PipelineLayout>
      </Page>
    );
  }

  if (!pipeline.currentVersion.zipfile) {
    return (
      <Page title={pipeline.name ?? t("Pipeline Code")}>
        <PipelineLayout
          workspace={workspace}
          pipeline={pipeline}
          currentTab="code"
        >
          <div className="flex items-center justify-center h-64">
            <div className="text-center">
              <div className="text-gray-500 text-lg mb-2">
                {t("No source code available")}
              </div>
              <div className="text-gray-400 text-sm">
                {t("This pipeline version doesn't contain source code.")}
              </div>
            </div>
          </div>
        </PipelineLayout>
      </Page>
    );
  }

  return (
    <Page title={pipeline.name ?? t("Pipeline Code")}>
      <PipelineLayout
        workspace={workspace}
        pipeline={pipeline}
        currentTab="code"
      >
        <PipelineCodeViewer
          versionId={pipeline.currentVersion.id}
          versionName={pipeline.currentVersion.versionName}
        />
      </PipelineLayout>
    </Page>
  );
};

WorkspacePipelineCodePage.getLayout = (page) => page;

export const getServerSideProps = createGetServerSideProps({
  requireAuth: true,
  async getServerSideProps(ctx, client) {
    await PipelineLayout.prefetch(ctx, client);

    const { data } = await client.query<
      WorkspacePipelineCodePageQuery,
      WorkspacePipelineCodePageQueryVariables
    >({
      query: WorkspacePipelineCodePageDocument,
      variables: {
        workspaceSlug: ctx.params!.workspaceSlug as string,
        pipelineCode: ctx.params!.pipelineCode as string,
      },
    });

    if (!data.workspace || !data.pipeline) {
      return { notFound: true };
    }

    return {
      props: {
        workspaceSlug: ctx.params!.workspaceSlug,
        pipelineCode: ctx.params!.pipelineCode,
      },
    };
  },
});

export default WorkspacePipelineCodePage;

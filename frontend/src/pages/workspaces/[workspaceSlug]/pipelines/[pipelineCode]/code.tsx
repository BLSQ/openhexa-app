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

const WorkspacePipelineCodePage: NextPageWithLayout = (props: Props) => {
  const { pipelineCode, workspaceSlug } = props;
  const { t } = useTranslation();

  const { data } = useWorkspacePipelineCodePageQuery({
    variables: {
      workspaceSlug,
      pipelineCode,
    },
  });

  if (!data?.workspace || !data?.pipeline) {
    return null;
  }
  const { workspace, pipeline } = data;

  if (!pipeline.currentVersion) {
    return null;
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

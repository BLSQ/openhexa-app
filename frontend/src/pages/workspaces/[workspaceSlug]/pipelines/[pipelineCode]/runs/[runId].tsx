import { createGetServerSideProps } from "core/helpers/page";
import { NextPageWithLayout } from "core/helpers/types";
import PipelineDetailPage from "pipelines/features/PipelineDetail/PipelineDetailPage";
import {
  WorkspacePipelineDetailPageDocument,
  WorkspacePipelineDetailPageQuery,
  WorkspacePipelineDetailPageQueryVariables,
  WorkspacePipelineRunPageDocument,
  WorkspacePipelineRunPageQuery,
  WorkspacePipelineRunPageQueryVariables,
} from "workspaces/graphql/queries.generated";
import WorkspaceLayout from "workspaces/layouts/WorkspaceLayout";

type Props = {
  workspaceSlug: string;
  pipelineCode: string;
  runId: string;
};

const WorkspacePipelineRunPage: NextPageWithLayout = (props: Props) => (
  <PipelineDetailPage
    workspaceSlug={props.workspaceSlug}
    pipelineCode={props.pipelineCode}
    runId={props.runId}
  />
);

WorkspacePipelineRunPage.getLayout = (page) => page;

export const getServerSideProps = createGetServerSideProps({
  requireAuth: true,
  async getServerSideProps(ctx, client) {
    await WorkspaceLayout.prefetch(ctx, client);
    const workspaceSlug = ctx.params?.workspaceSlug as string;
    const runId = ctx.params?.runId as string;

    const { data } = await client.query<
      WorkspacePipelineRunPageQuery,
      WorkspacePipelineRunPageQueryVariables
    >({
      query: WorkspacePipelineRunPageDocument,
      variables: { workspaceSlug, runId },
    });

    if (!data.workspace || !data.pipelineRun) {
      return {
        notFound: true,
      };
    }

    // The [pipelineCode] segment is not always the code (some links use the
    // pipeline id), so the run itself tells us which pipeline to load.
    const pipelineCode = data.pipelineRun.pipeline.code;

    await client.query<
      WorkspacePipelineDetailPageQuery,
      WorkspacePipelineDetailPageQueryVariables
    >({
      query: WorkspacePipelineDetailPageDocument,
      variables: { workspaceSlug, pipelineCode },
    });

    return {
      props: {
        workspaceSlug,
        pipelineCode,
        runId,
      },
    };
  },
});

export default WorkspacePipelineRunPage;

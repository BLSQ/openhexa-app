import { createGetServerSideProps } from "core/helpers/page";
import { NextPageWithLayout } from "core/helpers/types";
import PipelineDetailPage from "pipelines/features/PipelineDetail/PipelineDetailPage";
import {
  WorkspacePipelineDetailPageDocument,
  WorkspacePipelineDetailPageQuery,
  WorkspacePipelineDetailPageQueryVariables,
} from "workspaces/graphql/queries.generated";
import WorkspaceLayout from "workspaces/layouts/WorkspaceLayout";

type Props = {
  pipelineCode: string;
  workspaceSlug: string;
};

const WorkspacePipelinePage: NextPageWithLayout = (props: Props) => (
  <PipelineDetailPage
    workspaceSlug={props.workspaceSlug}
    pipelineCode={props.pipelineCode}
  />
);

WorkspacePipelinePage.getLayout = (page) => page;

export const getServerSideProps = createGetServerSideProps({
  requireAuth: true,
  async getServerSideProps(ctx, client) {
    await WorkspaceLayout.prefetch(ctx, client);

    const { data } = await client.query<
      WorkspacePipelineDetailPageQuery,
      WorkspacePipelineDetailPageQueryVariables
    >({
      query: WorkspacePipelineDetailPageDocument,
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

export default WorkspacePipelinePage;

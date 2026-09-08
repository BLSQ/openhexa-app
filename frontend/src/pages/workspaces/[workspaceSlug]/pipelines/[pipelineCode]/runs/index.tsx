import { GetServerSideProps } from "next";

// The pipeline detail page is now a single page with in-page views; this route
// is kept so existing links and bookmarks land on the matching tab.
export const getServerSideProps: GetServerSideProps = async (ctx) => {
  const workspaceSlug = encodeURIComponent(ctx.params!.workspaceSlug as string);
  const pipelineCode = encodeURIComponent(ctx.params!.pipelineCode as string);

  return {
    redirect: {
      destination: `/workspaces/${workspaceSlug}/pipelines/${pipelineCode}?tab=runs`,
      permanent: false,
    },
  };
};

const WorkspacePipelineRunsRedirect = () => null;

export default WorkspacePipelineRunsRedirect;

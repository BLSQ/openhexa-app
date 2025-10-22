import { graphql } from "graphql/gql";

export const PipelineDeletePipelineDoc = graphql(`
fragment PipelineDelete_pipeline on Pipeline {
  id
  name
  code
}
`);

export const PipelineDeleteWorkspaceDoc = graphql(`
fragment PipelineDelete_workspace on Workspace {
  slug
}
`);

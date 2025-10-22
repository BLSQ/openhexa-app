import { graphql } from "graphql/gql";

export const PipelineTemplatesWorkspaceDoc = graphql(`
fragment PipelineTemplates_workspace on Workspace {
  slug
}
`);

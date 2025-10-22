import { graphql } from "graphql/gql";

export const PipelinesWorkspaceDoc = graphql(`
fragment Pipelines_workspace on Workspace {
  slug
}
`);

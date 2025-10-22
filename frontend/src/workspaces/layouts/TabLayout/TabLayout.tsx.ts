import { graphql } from "graphql/gql";

export const TabLayoutWorkspaceDoc = graphql(`
fragment TabLayout_workspace on Workspace {
  ...WorkspaceLayout_workspace
  name
}
`);

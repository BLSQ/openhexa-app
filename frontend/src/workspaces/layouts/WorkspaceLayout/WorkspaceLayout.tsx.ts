import { graphql } from "graphql/gql";

export const WorkspaceLayoutWorkspaceDoc = graphql(`
fragment WorkspaceLayout_workspace on Workspace {
  slug
  ...Sidebar_workspace
}
`);

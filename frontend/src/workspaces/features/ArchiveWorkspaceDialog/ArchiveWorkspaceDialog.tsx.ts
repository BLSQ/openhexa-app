import { graphql } from "graphql/gql";

export const ArchiveWorkspaceWorkspaceDoc = graphql(`
fragment ArchiveWorkspace_workspace on Workspace {
  slug
  name
}
`);

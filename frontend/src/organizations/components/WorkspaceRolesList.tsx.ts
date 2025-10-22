import { graphql } from "graphql/gql";

export const WorkspaceRoleDoc = graphql(`
fragment WorkspaceRole on WorkspaceMembership {
  role
  workspace {
    name
    slug
  }
}
`);

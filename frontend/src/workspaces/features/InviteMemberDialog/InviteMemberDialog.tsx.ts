import { graphql } from "graphql/gql";

export const InviteMemberWorkspaceWorkspaceDoc = graphql(`
fragment InviteMemberWorkspace_workspace on Workspace {
  slug
  name
}
`);

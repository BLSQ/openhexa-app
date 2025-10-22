import { graphql } from "graphql/gql";

export const DeleteWorkspaceMemberWorkspaceMemberDoc = graphql(`
fragment DeleteWorkspaceMember_workspaceMember on WorkspaceMembership {
  id
  user {
    id
    displayName
  }
  organizationMembership {
    role
  }
}
`);

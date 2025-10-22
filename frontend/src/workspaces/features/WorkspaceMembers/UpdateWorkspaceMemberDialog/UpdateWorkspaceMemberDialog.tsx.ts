import { graphql } from "graphql/gql";

export const UpdateWorkspaceMemberWorkspaceMemberDoc = graphql(`
fragment UpdateWorkspaceMember_workspaceMember on WorkspaceMembership {
  id
  role
}
`);

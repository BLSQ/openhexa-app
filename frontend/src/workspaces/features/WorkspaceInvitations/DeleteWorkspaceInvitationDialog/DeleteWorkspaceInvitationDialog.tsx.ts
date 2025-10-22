import { graphql } from "graphql/gql";

export const DeleteWorkspaceInvitationWorkspaceInvitationDoc = graphql(`
fragment DeleteWorkspaceInvitation_workspaceInvitation on WorkspaceInvitation {
  id
  email
}
`);

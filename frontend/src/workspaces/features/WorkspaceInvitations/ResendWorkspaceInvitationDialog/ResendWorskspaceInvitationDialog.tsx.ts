import { graphql } from "graphql/gql";

export const ResendWorkspaceInvitationWorkspaceInvitationDoc = graphql(`
fragment ResendWorkspaceInvitation_workspaceInvitation on WorkspaceInvitation {
  id
  email
}
`);

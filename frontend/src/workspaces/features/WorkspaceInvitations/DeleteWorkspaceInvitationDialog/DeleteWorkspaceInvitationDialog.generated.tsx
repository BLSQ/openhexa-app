import * as Types from '../../../../graphql/types';

import { gql } from '@apollo/client';
export type DeleteWorkspaceInvitation_WorkspaceInvitationFragment = { __typename?: 'WorkspaceInvitation', id: string, email: string };

export const DeleteWorkspaceInvitation_WorkspaceInvitationFragmentDoc = gql`
    fragment DeleteWorkspaceInvitation_workspaceInvitation on WorkspaceInvitation {
  id
  email
}
    `;
import * as Types from '../../../../graphql/types';

import { gql } from '@apollo/client';
export type ResendWorkspaceInvitation_WorkspaceInvitationFragment = { __typename?: 'WorkspaceInvitation', id: string, email: string };

export const ResendWorkspaceInvitation_WorkspaceInvitationFragmentDoc = gql`
    fragment ResendWorkspaceInvitation_workspaceInvitation on WorkspaceInvitation {
  id
  email
}
    `;
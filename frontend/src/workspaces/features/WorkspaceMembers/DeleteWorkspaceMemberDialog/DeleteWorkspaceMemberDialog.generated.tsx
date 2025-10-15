import * as Types from '../../../../graphql/types';

import { gql } from '@apollo/client';
export type DeleteWorkspaceMember_WorkspaceMemberFragment = { __typename?: 'WorkspaceMembership', id: string, user: { __typename?: 'User', id: string, displayName: string }, organizationMembership?: { __typename?: 'OrganizationMembership', role: Types.OrganizationMembershipRole } | null };

export const DeleteWorkspaceMember_WorkspaceMemberFragmentDoc = gql`
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
    `;
import * as Types from '../../../../graphql/types';

import { gql } from '@apollo/client';
export type UpdateWorkspaceMember_WorkspaceMemberFragment = { __typename?: 'WorkspaceMembership', id: string, role: Types.WorkspaceMembershipRole };

export const UpdateWorkspaceMember_WorkspaceMemberFragmentDoc = gql`
    fragment UpdateWorkspaceMember_workspaceMember on WorkspaceMembership {
  id
  role
}
    `;
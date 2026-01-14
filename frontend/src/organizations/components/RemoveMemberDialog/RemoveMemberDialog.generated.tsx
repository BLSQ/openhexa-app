import * as Types from '../../../graphql/types';

import { gql } from '@apollo/client';
export type RemoveMemberDialog_Member_ExternalCollaborator_Fragment = { __typename?: 'ExternalCollaborator', id: string, user: { __typename?: 'User', id: string, displayName: string } };

export type RemoveMemberDialog_Member_OrganizationMembership_Fragment = { __typename?: 'OrganizationMembership', role: Types.OrganizationMembershipRole, id: string, user: { __typename?: 'User', id: string, displayName: string } };

export type RemoveMemberDialog_MemberFragment = RemoveMemberDialog_Member_ExternalCollaborator_Fragment | RemoveMemberDialog_Member_OrganizationMembership_Fragment;

export const RemoveMemberDialog_MemberFragmentDoc = gql`
    fragment RemoveMemberDialog_member on OrganizationMember {
  id
  user {
    id
    displayName
  }
  ... on OrganizationMembership {
    role
  }
}
    `;
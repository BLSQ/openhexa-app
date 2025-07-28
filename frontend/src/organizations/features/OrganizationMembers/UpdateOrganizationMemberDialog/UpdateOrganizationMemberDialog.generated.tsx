import * as Types from '../../../../graphql/types';

import { gql } from '@apollo/client';
export type UpdateOrganizationMemberDialog_OrganizationMemberFragment = { __typename?: 'OrganizationMembership', id: string, role: Types.OrganizationMembershipRole, workspaceMemberships: Array<{ __typename?: 'WorkspaceMembership', id: string, role: Types.WorkspaceMembershipRole, workspace: { __typename?: 'Workspace', slug: string, name: string } }>, user: { __typename?: 'User', id: string, displayName: string, email: string } };

export type UpdateOrganizationMemberDialog_WorkspaceFragment = { __typename?: 'Workspace', slug: string, name: string };

export const UpdateOrganizationMemberDialog_OrganizationMemberFragmentDoc = gql`
    fragment UpdateOrganizationMemberDialog_organizationMember on OrganizationMembership {
  id
  role
  workspaceMemberships {
    id
    role
    workspace {
      slug
      name
    }
  }
  user {
    id
    displayName
    email
  }
}
    `;
export const UpdateOrganizationMemberDialog_WorkspaceFragmentDoc = gql`
    fragment UpdateOrganizationMemberDialog_workspace on Workspace {
  slug
  name
}
    `;
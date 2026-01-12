import * as Types from '../../../graphql/types';

import { gql } from '@apollo/client';
export type UpdateMemberPermissionsDialog_Member_ExternalCollaborator_Fragment = { __typename?: 'ExternalCollaborator', id: string, workspaceMemberships: Array<{ __typename?: 'WorkspaceMembership', id: string, role: Types.WorkspaceMembershipRole, workspace: { __typename?: 'Workspace', slug: string, name: string } }>, user: { __typename?: 'User', id: string, displayName: string, email: string } };

export type UpdateMemberPermissionsDialog_Member_OrganizationMembership_Fragment = { __typename?: 'OrganizationMembership', role: Types.OrganizationMembershipRole, id: string, workspaceMemberships: Array<{ __typename?: 'WorkspaceMembership', id: string, role: Types.WorkspaceMembershipRole, workspace: { __typename?: 'Workspace', slug: string, name: string } }>, user: { __typename?: 'User', id: string, displayName: string, email: string } };

export type UpdateMemberPermissionsDialog_MemberFragment = UpdateMemberPermissionsDialog_Member_ExternalCollaborator_Fragment | UpdateMemberPermissionsDialog_Member_OrganizationMembership_Fragment;

export type UpdateMemberPermissionsDialog_WorkspaceFragment = { __typename?: 'Workspace', slug: string, name: string };

export const UpdateMemberPermissionsDialog_MemberFragmentDoc = gql`
    fragment UpdateMemberPermissionsDialog_member on OrganizationMember {
  id
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
  ... on OrganizationMembership {
    role
  }
}
    `;
export const UpdateMemberPermissionsDialog_WorkspaceFragmentDoc = gql`
    fragment UpdateMemberPermissionsDialog_workspace on Workspace {
  slug
  name
}
    `;
import * as Types from '../../graphql/types';

import { gql } from '@apollo/client';
export type WorkspaceRoleFragment = { __typename?: 'WorkspaceMembership', role: Types.WorkspaceMembershipRole, workspace: { __typename?: 'Workspace', name: string, slug: string } };

export const WorkspaceRoleFragmentDoc = gql`
    fragment WorkspaceRole on WorkspaceMembership {
  role
  workspace {
    name
    slug
  }
}
    `;
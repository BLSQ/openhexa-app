import * as Types from '../../../graphql/types';

import { gql } from '@apollo/client';
export type WorkspaceMemberPicker_WorkspaceFragment = { __typename?: 'Workspace', slug: string, members: { __typename?: 'WorkspaceMembershipPage', items: Array<{ __typename?: 'WorkspaceMembership', id: string, user: { __typename?: 'User', id: string, displayName: string } }> } };

export const WorkspaceMemberPicker_WorkspaceFragmentDoc = gql`
    fragment WorkspaceMemberPicker_workspace on Workspace {
  slug
  members {
    items {
      id
      user {
        id
        displayName
      }
    }
  }
}
    `;
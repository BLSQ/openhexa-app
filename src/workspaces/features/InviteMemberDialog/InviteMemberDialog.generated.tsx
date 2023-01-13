import * as Types from '../../../graphql-types';

import { gql } from '@apollo/client';
export type InviteMemberWorkspace_WorkspaceFragment = { __typename?: 'Workspace', id: string, name: string };

export const InviteMemberWorkspace_WorkspaceFragmentDoc = gql`
    fragment InviteMemberWorkspace_workspace on Workspace {
  id
  name
}
    `;
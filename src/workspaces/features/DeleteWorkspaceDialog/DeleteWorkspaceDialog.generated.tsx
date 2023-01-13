import * as Types from '../../../graphql-types';

import { gql } from '@apollo/client';
export type DeleteWorkspace_WorkspaceFragment = { __typename?: 'Workspace', id: string, name: string };

export const DeleteWorkspace_WorkspaceFragmentDoc = gql`
    fragment DeleteWorkspace_workspace on Workspace {
  id
  name
}
    `;
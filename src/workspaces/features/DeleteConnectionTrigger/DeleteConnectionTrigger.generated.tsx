import * as Types from '../../../graphql/types';

import { gql } from '@apollo/client';
export type DeleteConnectionTrigger_WorkspaceFragment = { __typename?: 'Workspace', slug: string };

export type DeleteConnectionTrigger_ConnectionFragment = { __typename?: 'Connection', id: string, name: string, permissions: { __typename?: 'ConnectionPermissions', delete: boolean } };

export const DeleteConnectionTrigger_WorkspaceFragmentDoc = gql`
    fragment DeleteConnectionTrigger_workspace on Workspace {
  slug
}
    `;
export const DeleteConnectionTrigger_ConnectionFragmentDoc = gql`
    fragment DeleteConnectionTrigger_connection on Connection {
  id
  name
  permissions {
    delete
  }
}
    `;
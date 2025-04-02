import * as Types from '../../../graphql/types';

import { gql } from '@apollo/client';
export type DatabaseTableDeleteTrigger_WorkspaceFragment = { __typename?: 'Workspace', slug: string, permissions: { __typename?: 'WorkspacePermissions', deleteDatabaseTable: boolean } };

export type DatabaseTableDeleteTrigger_DatabaseFragment = { __typename?: 'DatabaseTable', name: string };

export const DatabaseTableDeleteTrigger_WorkspaceFragmentDoc = gql`
    fragment DatabaseTableDeleteTrigger_workspace on Workspace {
  slug
  permissions {
    deleteDatabaseTable
  }
}
    `;
export const DatabaseTableDeleteTrigger_DatabaseFragmentDoc = gql`
    fragment DatabaseTableDeleteTrigger_database on DatabaseTable {
  name
}
    `;
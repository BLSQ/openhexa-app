import * as Types from '../../../graphql/types';

import { gql } from '@apollo/client';
export type DeleteConnectionTrigger_WorkspaceFragment = { __typename?: 'Workspace', slug: string };

export type DeleteConnectionTrigger_Connection_CustomConnection_Fragment = { __typename?: 'CustomConnection', id: string, name: string, permissions: { __typename?: 'ConnectionPermissions', delete: boolean } };

export type DeleteConnectionTrigger_Connection_Dhis2Connection_Fragment = { __typename?: 'DHIS2Connection', id: string, name: string, permissions: { __typename?: 'ConnectionPermissions', delete: boolean } };

export type DeleteConnectionTrigger_Connection_GcsConnection_Fragment = { __typename?: 'GCSConnection', id: string, name: string, permissions: { __typename?: 'ConnectionPermissions', delete: boolean } };

export type DeleteConnectionTrigger_Connection_IasoConnection_Fragment = { __typename?: 'IASOConnection', id: string, name: string, permissions: { __typename?: 'ConnectionPermissions', delete: boolean } };

export type DeleteConnectionTrigger_Connection_PostgreSqlConnection_Fragment = { __typename?: 'PostgreSQLConnection', id: string, name: string, permissions: { __typename?: 'ConnectionPermissions', delete: boolean } };

export type DeleteConnectionTrigger_Connection_S3Connection_Fragment = { __typename?: 'S3Connection', id: string, name: string, permissions: { __typename?: 'ConnectionPermissions', delete: boolean } };

export type DeleteConnectionTrigger_ConnectionFragment = DeleteConnectionTrigger_Connection_CustomConnection_Fragment | DeleteConnectionTrigger_Connection_Dhis2Connection_Fragment | DeleteConnectionTrigger_Connection_GcsConnection_Fragment | DeleteConnectionTrigger_Connection_IasoConnection_Fragment | DeleteConnectionTrigger_Connection_PostgreSqlConnection_Fragment | DeleteConnectionTrigger_Connection_S3Connection_Fragment;

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
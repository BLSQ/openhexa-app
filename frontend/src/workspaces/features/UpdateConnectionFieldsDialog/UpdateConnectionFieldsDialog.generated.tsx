import * as Types from '../../../graphql/types';

import { gql } from '@apollo/client';
export type UpdateConnectionFieldsDialog_Connection_CustomConnection_Fragment = { __typename?: 'CustomConnection', id: string, name: string, type: Types.ConnectionType, fields: Array<{ __typename?: 'ConnectionField', code: string, value?: string | null, secret: boolean }> };

export type UpdateConnectionFieldsDialog_Connection_Dhis2Connection_Fragment = { __typename?: 'DHIS2Connection', id: string, name: string, type: Types.ConnectionType, fields: Array<{ __typename?: 'ConnectionField', code: string, value?: string | null, secret: boolean }> };

export type UpdateConnectionFieldsDialog_Connection_GcsConnection_Fragment = { __typename?: 'GCSConnection', id: string, name: string, type: Types.ConnectionType, fields: Array<{ __typename?: 'ConnectionField', code: string, value?: string | null, secret: boolean }> };

export type UpdateConnectionFieldsDialog_Connection_IasoConnection_Fragment = { __typename?: 'IASOConnection', id: string, name: string, type: Types.ConnectionType, fields: Array<{ __typename?: 'ConnectionField', code: string, value?: string | null, secret: boolean }> };

export type UpdateConnectionFieldsDialog_Connection_PostgreSqlConnection_Fragment = { __typename?: 'PostgreSQLConnection', id: string, name: string, type: Types.ConnectionType, fields: Array<{ __typename?: 'ConnectionField', code: string, value?: string | null, secret: boolean }> };

export type UpdateConnectionFieldsDialog_Connection_S3Connection_Fragment = { __typename?: 'S3Connection', id: string, name: string, type: Types.ConnectionType, fields: Array<{ __typename?: 'ConnectionField', code: string, value?: string | null, secret: boolean }> };

export type UpdateConnectionFieldsDialog_ConnectionFragment = UpdateConnectionFieldsDialog_Connection_CustomConnection_Fragment | UpdateConnectionFieldsDialog_Connection_Dhis2Connection_Fragment | UpdateConnectionFieldsDialog_Connection_GcsConnection_Fragment | UpdateConnectionFieldsDialog_Connection_IasoConnection_Fragment | UpdateConnectionFieldsDialog_Connection_PostgreSqlConnection_Fragment | UpdateConnectionFieldsDialog_Connection_S3Connection_Fragment;

export const UpdateConnectionFieldsDialog_ConnectionFragmentDoc = gql`
    fragment UpdateConnectionFieldsDialog_connection on Connection {
  id
  name
  type
  fields {
    code
    value
    secret
  }
}
    `;
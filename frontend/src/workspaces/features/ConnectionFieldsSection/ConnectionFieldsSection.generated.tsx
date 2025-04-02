import * as Types from '../../../graphql/types';

import { gql } from '@apollo/client';
import { UpdateConnectionFieldsDialog_ConnectionFragmentDoc } from '../UpdateConnectionFieldsDialog/UpdateConnectionFieldsDialog.generated';
export type ConnectionFieldsSection_Connection_CustomConnection_Fragment = { __typename?: 'CustomConnection', id: string, type: Types.ConnectionType, slug: string, name: string, fields: Array<{ __typename?: 'ConnectionField', code: string, value?: string | null, secret: boolean }>, permissions: { __typename?: 'ConnectionPermissions', update: boolean } };

export type ConnectionFieldsSection_Connection_Dhis2Connection_Fragment = { __typename?: 'DHIS2Connection', id: string, type: Types.ConnectionType, slug: string, name: string, fields: Array<{ __typename?: 'ConnectionField', code: string, value?: string | null, secret: boolean }>, permissions: { __typename?: 'ConnectionPermissions', update: boolean } };

export type ConnectionFieldsSection_Connection_GcsConnection_Fragment = { __typename?: 'GCSConnection', id: string, type: Types.ConnectionType, slug: string, name: string, fields: Array<{ __typename?: 'ConnectionField', code: string, value?: string | null, secret: boolean }>, permissions: { __typename?: 'ConnectionPermissions', update: boolean } };

export type ConnectionFieldsSection_Connection_IasoConnection_Fragment = { __typename?: 'IASOConnection', id: string, type: Types.ConnectionType, slug: string, name: string, fields: Array<{ __typename?: 'ConnectionField', code: string, value?: string | null, secret: boolean }>, permissions: { __typename?: 'ConnectionPermissions', update: boolean } };

export type ConnectionFieldsSection_Connection_PostgreSqlConnection_Fragment = { __typename?: 'PostgreSQLConnection', id: string, type: Types.ConnectionType, slug: string, name: string, fields: Array<{ __typename?: 'ConnectionField', code: string, value?: string | null, secret: boolean }>, permissions: { __typename?: 'ConnectionPermissions', update: boolean } };

export type ConnectionFieldsSection_Connection_S3Connection_Fragment = { __typename?: 'S3Connection', id: string, type: Types.ConnectionType, slug: string, name: string, fields: Array<{ __typename?: 'ConnectionField', code: string, value?: string | null, secret: boolean }>, permissions: { __typename?: 'ConnectionPermissions', update: boolean } };

export type ConnectionFieldsSection_ConnectionFragment = ConnectionFieldsSection_Connection_CustomConnection_Fragment | ConnectionFieldsSection_Connection_Dhis2Connection_Fragment | ConnectionFieldsSection_Connection_GcsConnection_Fragment | ConnectionFieldsSection_Connection_IasoConnection_Fragment | ConnectionFieldsSection_Connection_PostgreSqlConnection_Fragment | ConnectionFieldsSection_Connection_S3Connection_Fragment;

export const ConnectionFieldsSection_ConnectionFragmentDoc = gql`
    fragment ConnectionFieldsSection_connection on Connection {
  id
  type
  slug
  fields {
    code
    value
    secret
  }
  permissions {
    update
  }
  ...UpdateConnectionFieldsDialog_connection
}
    ${UpdateConnectionFieldsDialog_ConnectionFragmentDoc}`;
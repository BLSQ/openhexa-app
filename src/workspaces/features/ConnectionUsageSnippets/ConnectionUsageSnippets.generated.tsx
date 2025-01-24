import * as Types from '../../../graphql/types';

import { gql } from '@apollo/client';
export type ConnectionUsageSnippets_Connection_CustomConnection_Fragment = { __typename?: 'CustomConnection', id: string, type: Types.ConnectionType, slug: string, fields: Array<{ __typename?: 'ConnectionField', code: string }> };

export type ConnectionUsageSnippets_Connection_Dhis2Connection_Fragment = { __typename?: 'DHIS2Connection', id: string, type: Types.ConnectionType, slug: string, fields: Array<{ __typename?: 'ConnectionField', code: string }> };

export type ConnectionUsageSnippets_Connection_GcsConnection_Fragment = { __typename?: 'GCSConnection', id: string, type: Types.ConnectionType, slug: string, fields: Array<{ __typename?: 'ConnectionField', code: string }> };

export type ConnectionUsageSnippets_Connection_IasoConnection_Fragment = { __typename?: 'IASOConnection', id: string, type: Types.ConnectionType, slug: string, fields: Array<{ __typename?: 'ConnectionField', code: string }> };

export type ConnectionUsageSnippets_Connection_PostgreSqlConnection_Fragment = { __typename?: 'PostgreSQLConnection', id: string, type: Types.ConnectionType, slug: string, fields: Array<{ __typename?: 'ConnectionField', code: string }> };

export type ConnectionUsageSnippets_Connection_S3Connection_Fragment = { __typename?: 'S3Connection', id: string, type: Types.ConnectionType, slug: string, fields: Array<{ __typename?: 'ConnectionField', code: string }> };

export type ConnectionUsageSnippets_ConnectionFragment = ConnectionUsageSnippets_Connection_CustomConnection_Fragment | ConnectionUsageSnippets_Connection_Dhis2Connection_Fragment | ConnectionUsageSnippets_Connection_GcsConnection_Fragment | ConnectionUsageSnippets_Connection_IasoConnection_Fragment | ConnectionUsageSnippets_Connection_PostgreSqlConnection_Fragment | ConnectionUsageSnippets_Connection_S3Connection_Fragment;

export const ConnectionUsageSnippets_ConnectionFragmentDoc = gql`
    fragment ConnectionUsageSnippets_connection on Connection {
  id
  type
  slug
  fields {
    code
  }
}
    `;
import * as Types from '../../../graphql-types';

import { gql } from '@apollo/client';
export type ConnectionFieldsSection_ConnectionFragment = { __typename?: 'Connection', id: string, type: Types.ConnectionType, fields: Array<{ __typename?: 'ConnectionField', code: string, value?: string | null, secret: boolean }>, permissions: { __typename?: 'ConnectionPermissions', update: boolean } };

export const ConnectionFieldsSection_ConnectionFragmentDoc = gql`
    fragment ConnectionFieldsSection_connection on Connection {
  id
  type
  fields {
    code
    value
    secret
  }
  permissions {
    update
  }
}
    `;
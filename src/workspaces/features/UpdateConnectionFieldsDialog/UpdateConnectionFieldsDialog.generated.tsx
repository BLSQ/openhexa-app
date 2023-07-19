import * as Types from '../../../graphql-types';

import { gql } from '@apollo/client';
export type UpdateConnectionFieldsDialog_ConnectionFragment = { __typename?: 'Connection', id: string, name: string, type: Types.ConnectionType, fields: Array<{ __typename?: 'ConnectionField', code: string, value?: string | null, secret: boolean }> };

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
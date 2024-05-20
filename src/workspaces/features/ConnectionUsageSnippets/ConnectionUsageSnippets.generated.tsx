import * as Types from '../../../graphql/types';

import { gql } from '@apollo/client';
export type ConnectionUsageSnippets_ConnectionFragment = { __typename?: 'Connection', id: string, type: Types.ConnectionType, slug: string, fields: Array<{ __typename?: 'ConnectionField', code: string }> };

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
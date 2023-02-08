import * as Types from '../../../graphql-types';

import { gql } from '@apollo/client';
export type ConnectionFieldDialog_FieldFragment = { __typename?: 'ConnectionField', code: string, value?: string | null, secret: boolean };

export const ConnectionFieldDialog_FieldFragmentDoc = gql`
    fragment ConnectionFieldDialog_field on ConnectionField {
  code
  value
  secret
}
    `;
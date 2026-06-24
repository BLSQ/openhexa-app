import * as Types from '../../../graphql/types';

import { gql } from '@apollo/client';
export type WebappApiAccess_WebappFragment = { __typename?: 'Webapp', id: string, serveUrl: string, allowedOperations: Array<Types.WebappOperationScope>, permissions: { __typename?: 'WebappPermissions', update: boolean } };

export const WebappApiAccess_WebappFragmentDoc = gql`
    fragment WebappApiAccess_webapp on Webapp {
  id
  serveUrl
  allowedOperations
  permissions {
    update
  }
}
    `;
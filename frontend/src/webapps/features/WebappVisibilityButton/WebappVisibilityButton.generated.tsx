import * as Types from '../../../graphql/types';

import { gql } from '@apollo/client';
export type WebappVisibilityButton_WebappFragment = { __typename?: 'Webapp', id: string, type: Types.WebappType, isPublic: boolean, serveUrl: string, permissions: { __typename?: 'WebappPermissions', update: boolean } };

export const WebappVisibilityButton_WebappFragmentDoc = gql`
    fragment WebappVisibilityButton_webapp on Webapp {
  id
  type
  isPublic
  serveUrl
  permissions {
    update
  }
}
    `;
import * as Types from '../../../graphql/types';

import { gql } from '@apollo/client';
export type WebappCard_WebappFragment = { __typename?: 'Webapp', id: string, icon?: string | null, name: string, workspace: { __typename?: 'Workspace', slug: string, name: string } };

export const WebappCard_WebappFragmentDoc = gql`
    fragment WebappCard_webapp on Webapp {
  id
  icon
  name
  workspace {
    slug
    name
  }
}
    `;
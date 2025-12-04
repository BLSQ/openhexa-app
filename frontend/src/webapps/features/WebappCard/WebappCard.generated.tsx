import * as Types from '../../../graphql/types';

import { gql } from '@apollo/client';
export type WebappCard_WebappFragment = { __typename?: 'Webapp', id: string, slug: string, icon?: string | null, name: string, type: Types.WebappType, workspace: { __typename?: 'Workspace', slug: string, name: string } };

export const WebappCard_WebappFragmentDoc = gql`
    fragment WebappCard_webapp on Webapp {
  id
  slug
  icon
  name
  type
  workspace {
    slug
    name
  }
}
    `;
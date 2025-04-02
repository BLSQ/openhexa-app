import * as Types from '../../../graphql/types';

import { gql } from '@apollo/client';
export type WebappDelete_WebappFragment = { __typename?: 'Webapp', id: string, name: string };

export type WebappDelete_WorkspaceFragment = { __typename?: 'Workspace', slug: string };

export const WebappDelete_WebappFragmentDoc = gql`
    fragment WebappDelete_webapp on Webapp {
  id
  name
}
    `;
export const WebappDelete_WorkspaceFragmentDoc = gql`
    fragment WebappDelete_workspace on Workspace {
  slug
}
    `;
import * as Types from '../../../graphql/types';

import { gql } from '@apollo/client';
export type Pipelines_WorkspaceFragment = { __typename?: 'Workspace', slug: string };

export const Pipelines_WorkspaceFragmentDoc = gql`
    fragment Pipelines_workspace on Workspace {
  slug
}
    `;
import * as Types from '../../../graphql/types';

import { gql } from '@apollo/client';
export type CreateConnectionDialog_WorkspaceFragment = { __typename?: 'Workspace', slug: string };

export const CreateConnectionDialog_WorkspaceFragmentDoc = gql`
    fragment CreateConnectionDialog_workspace on Workspace {
  slug
}
    `;
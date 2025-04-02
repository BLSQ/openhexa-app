import * as Types from '../../../graphql/types';

import { gql } from '@apollo/client';
export type GenerateWorkspaceDatabasePasswordDialog_WorkspaceFragment = { __typename?: 'Workspace', slug: string };

export const GenerateWorkspaceDatabasePasswordDialog_WorkspaceFragmentDoc = gql`
    fragment GenerateWorkspaceDatabasePasswordDialog_workspace on Workspace {
  slug
}
    `;
import * as Types from '../../../graphql/types';

import { gql } from '@apollo/client';
export type ArchiveWorkspace_WorkspaceFragment = { __typename?: 'Workspace', slug: string, name: string };

export const ArchiveWorkspace_WorkspaceFragmentDoc = gql`
    fragment ArchiveWorkspace_workspace on Workspace {
  slug
  name
}
    `;
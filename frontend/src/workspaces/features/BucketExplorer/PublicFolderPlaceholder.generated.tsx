import * as Types from '../../../graphql/types';

import { gql } from '@apollo/client';
export type PublicFolderPlaceholder_WorkspaceFragment = { __typename?: 'Workspace', slug: string, publicFiles?: { __typename?: 'WorkspacePublicFiles', url?: string | null, folderExists: boolean } | null, permissions: { __typename?: 'WorkspacePermissions', createObject: boolean, managePublicFiles: boolean } };

export const PublicFolderPlaceholder_WorkspaceFragmentDoc = gql`
    fragment PublicFolderPlaceholder_workspace on Workspace {
  slug
  publicFiles {
    url
    folderExists
  }
  permissions {
    createObject
    managePublicFiles
  }
}
    `;
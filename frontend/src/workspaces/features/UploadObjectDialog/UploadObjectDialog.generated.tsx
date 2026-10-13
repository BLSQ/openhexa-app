import * as Types from '../../../graphql/types';

import { gql } from '@apollo/client';
export type UploadObjectDialog_WorkspaceFragment = { __typename?: 'Workspace', slug: string, publicFilesEnabled: boolean, permissions: { __typename?: 'WorkspacePermissions', createObject: boolean } };

export const UploadObjectDialog_WorkspaceFragmentDoc = gql`
    fragment UploadObjectDialog_workspace on Workspace {
  slug
  publicFilesEnabled
  permissions {
    createObject
  }
}
    `;
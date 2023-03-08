import * as Types from '../../../graphql-types';

import { gql } from '@apollo/client';
export type UploadObjectDialog_WorkspaceFragment = { __typename?: 'Workspace', slug: string, permissions: { __typename?: 'WorkspacePermissions', createObject: boolean }, bucket: { __typename?: 'Bucket', name: string } };

export const UploadObjectDialog_WorkspaceFragmentDoc = gql`
    fragment UploadObjectDialog_workspace on Workspace {
  slug
  permissions {
    createObject
  }
  bucket {
    name
  }
}
    `;
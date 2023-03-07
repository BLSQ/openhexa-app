import * as Types from '../../../graphql-types';

import { gql } from '@apollo/client';
export type UploadObjectDialog_WorkspaceFragment = { __typename?: 'Workspace', slug: string, permissions: { __typename?: 'WorkspacePermissions', createObject: boolean }, bucket: { __typename?: 'Bucket', name: string } };

export type UploadObjectDialog_DirectoryFragment = { __typename?: 'BucketObject', key: string, name: string, type: Types.BucketObjectType };

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
export const UploadObjectDialog_DirectoryFragmentDoc = gql`
    fragment UploadObjectDialog_directory on BucketObject {
  key
  name
  type
}
    `;
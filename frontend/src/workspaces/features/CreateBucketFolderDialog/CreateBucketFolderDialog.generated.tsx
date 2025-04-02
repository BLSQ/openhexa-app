import * as Types from '../../../graphql/types';

import { gql } from '@apollo/client';
export type CreateBucketFolderDialog_WorkspaceFragment = { __typename?: 'Workspace', slug: string, permissions: { __typename?: 'WorkspacePermissions', createObject: boolean }, bucket: { __typename?: 'Bucket', name: string } };

export const CreateBucketFolderDialog_WorkspaceFragmentDoc = gql`
    fragment CreateBucketFolderDialog_workspace on Workspace {
  slug
  permissions {
    createObject
  }
  bucket {
    name
  }
}
    `;
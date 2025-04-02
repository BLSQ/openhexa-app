import * as Types from '../../../graphql/types';

import { gql } from '@apollo/client';
export type DeleteBucketObject_WorkspaceFragment = { __typename?: 'Workspace', slug: string, permissions: { __typename?: 'WorkspacePermissions', deleteObject: boolean } };

export type DeleteBucketObject_ObjectFragment = { __typename?: 'BucketObject', key: string, name: string, type: Types.BucketObjectType };

export const DeleteBucketObject_WorkspaceFragmentDoc = gql`
    fragment DeleteBucketObject_workspace on Workspace {
  slug
  permissions {
    deleteObject
  }
}
    `;
export const DeleteBucketObject_ObjectFragmentDoc = gql`
    fragment DeleteBucketObject_object on BucketObject {
  key
  name
  type
}
    `;
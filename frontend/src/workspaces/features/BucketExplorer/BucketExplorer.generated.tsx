import * as Types from '../../../graphql/types';

import { gql } from '@apollo/client';
import { DownloadBucketObject_WorkspaceFragmentDoc, DownloadBucketObject_ObjectFragmentDoc } from '../DownloadBucketObject/DownloadBucketObject.generated';
import { DeleteBucketObject_WorkspaceFragmentDoc, DeleteBucketObject_ObjectFragmentDoc } from '../DeleteBucketObject/DeleteBucketObject.generated';
export type BucketExplorer_WorkspaceFragment = { __typename?: 'Workspace', slug: string, permissions: { __typename?: 'WorkspacePermissions', deleteObject: boolean } };

export type BucketExplorer_ObjectsFragment = { __typename?: 'BucketObjectPage', hasNextPage: boolean, hasPreviousPage: boolean, pageNumber: number, items: Array<{ __typename?: 'BucketObject', key: string, name: string, path: string, size?: any | null, updatedAt?: any | null, type: Types.BucketObjectType }> };

export const BucketExplorer_WorkspaceFragmentDoc = gql`
    fragment BucketExplorer_workspace on Workspace {
  slug
  ...DownloadBucketObject_workspace
  ...DeleteBucketObject_workspace
}
    ${DownloadBucketObject_WorkspaceFragmentDoc}
${DeleteBucketObject_WorkspaceFragmentDoc}`;
export const BucketExplorer_ObjectsFragmentDoc = gql`
    fragment BucketExplorer_objects on BucketObjectPage {
  hasNextPage
  hasPreviousPage
  pageNumber
  items {
    key
    name
    path
    size
    updatedAt
    type
    ...DownloadBucketObject_object
    ...DeleteBucketObject_object
  }
}
    ${DownloadBucketObject_ObjectFragmentDoc}
${DeleteBucketObject_ObjectFragmentDoc}`;
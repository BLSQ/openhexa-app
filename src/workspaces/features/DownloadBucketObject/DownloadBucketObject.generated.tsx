import * as Types from '../../../graphql/types';

import { gql } from '@apollo/client';
export type DownloadBucketObject_WorkspaceFragment = { __typename?: 'Workspace', slug: string };

export type DownloadBucketObject_ObjectFragment = { __typename?: 'BucketObject', key: string };

export const DownloadBucketObject_WorkspaceFragmentDoc = gql`
    fragment DownloadBucketObject_workspace on Workspace {
  slug
}
    `;
export const DownloadBucketObject_ObjectFragmentDoc = gql`
    fragment DownloadBucketObject_object on BucketObject {
  key
}
    `;
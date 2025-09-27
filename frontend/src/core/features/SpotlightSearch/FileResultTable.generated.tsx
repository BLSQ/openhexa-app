import * as Types from '../../../graphql/types';

import { gql } from '@apollo/client';
import { WorkspaceDisplayFragmentFragmentDoc } from './WorkspaceDisplay.generated';
export type FilesPageFragment = { __typename?: 'BucketObjectResultPage', totalItems: number, pageNumber: number, totalPages: number, items: Array<{ __typename?: 'BucketObjectResult', score: number, file: { __typename?: 'BucketObject', name: string, path: string, size?: any | null, updatedAt?: any | null, type: Types.BucketObjectType }, workspace: { __typename?: 'Workspace', slug: string, name: string, countries: Array<{ __typename?: 'Country', code: string }> } }> };

export const FilesPageFragmentDoc = gql`
    fragment FilesPage on BucketObjectResultPage {
  items {
    file {
      name
      path
      size
      updatedAt
      type
    }
    score
    workspace {
      slug
      ...WorkspaceDisplayFragment
    }
  }
  totalItems
  pageNumber
  totalPages
}
    ${WorkspaceDisplayFragmentFragmentDoc}`;
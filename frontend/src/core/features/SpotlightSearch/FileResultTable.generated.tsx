import * as Types from '../../../graphql/types';

import { gql } from '@apollo/client';
import { WorkspaceDisplayFragmentFragmentDoc } from './WorkspaceDisplay.generated';
export type FilesPageFragment = { __typename?: 'FileResultPage', totalItems: number, pageNumber: number, totalPages: number, items: Array<{ __typename?: 'FileResult', score: number, file: { __typename?: 'File', name: string, path: string, size?: any | null, updatedAt?: any | null, type: Types.FileType }, workspace: { __typename?: 'Workspace', slug: string, name: string, countries: Array<{ __typename?: 'Country', code: string }> } }> };

export const FilesPageFragmentDoc = gql`
    fragment FilesPage on FileResultPage {
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
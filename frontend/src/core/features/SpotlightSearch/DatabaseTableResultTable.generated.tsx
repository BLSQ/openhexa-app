import * as Types from '../../../graphql/types';

import { gql } from '@apollo/client';
import { WorkspaceDisplayFragmentFragmentDoc } from './WorkspaceDisplay.generated';
export type DatabaseTablesPageFragment = { __typename?: 'DatabaseTableResultPage', totalItems: number, pageNumber: number, totalPages: number, items: Array<{ __typename?: 'DatabaseTableResult', score: number, databaseTable: { __typename?: 'DatabaseTable', name: string, count?: number | null }, workspace: { __typename?: 'Workspace', slug: string, name: string, countries: Array<{ __typename?: 'Country', code: string }> } }> };

export const DatabaseTablesPageFragmentDoc = gql`
    fragment DatabaseTablesPage on DatabaseTableResultPage {
  items {
    databaseTable {
      name
      count
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
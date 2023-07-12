import * as Types from '../../graphql-types';

import { gql } from '@apollo/client';
export type SearchResult_ResultFragment = { __typename?: 'SearchResult', rank: number, object: { __typename: 'CatalogEntry', id: string, name: string, objectId: string, objectUrl: any, symbol?: any | null, datasource?: { __typename?: 'Datasource', id: string, name: string } | null, type: { __typename?: 'CatalogEntryType', model: string, app: string, name: string } } };

export const SearchResult_ResultFragmentDoc = gql`
    fragment SearchResult_result on SearchResult {
  rank
  object {
    __typename
    ... on CatalogEntry {
      id
      name
      datasource {
        id
        name
      }
      type {
        model
        app
        name
      }
      objectId
      objectUrl
      symbol
    }
  }
}
    `;
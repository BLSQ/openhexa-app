import * as Types from '../../graphql-types';

import { gql } from '@apollo/client';
import { SearchResult_ResultFragmentDoc } from '../features/SearchResult.generated';
import * as Apollo from '@apollo/client';
const defaultOptions = {} as const;
export type SearchQueryQueryVariables = Types.Exact<{
  query?: Types.InputMaybe<Types.Scalars['String']>;
  types?: Types.InputMaybe<Array<Types.Scalars['String']> | Types.Scalars['String']>;
  datasourceIds?: Types.InputMaybe<Array<Types.Scalars['UUID']> | Types.Scalars['UUID']>;
  page?: Types.InputMaybe<Types.Scalars['Int']>;
  perPage?: Types.InputMaybe<Types.Scalars['Int']>;
}>;


export type SearchQueryQuery = { __typename?: 'Query', search: { __typename?: 'SearchQueryResult', results: Array<{ __typename?: 'SearchResult', rank: number, object: { __typename: 'CatalogEntry', id: string, name: string, objectId: string, objectUrl: any, symbol?: any | null, datasource?: { __typename?: 'Datasource', id: string, name: string } | null, type: { __typename?: 'CatalogEntryType', model: string, app: string, name: string } } | { __typename: 'Collection', id: string, name: string } }>, types: Array<{ __typename?: 'SearchType', value: string, label: string }> } };


export const SearchQueryDocument = gql`
    query SearchQuery($query: String, $types: [String!], $datasourceIds: [UUID!], $page: Int, $perPage: Int) {
  search(
    query: $query
    datasourceIds: $datasourceIds
    types: $types
    page: $page
    perPage: $perPage
  ) {
    results {
      ...SearchResult_result
    }
    types {
      value
      label
    }
  }
}
    ${SearchResult_ResultFragmentDoc}`;

/**
 * __useSearchQueryQuery__
 *
 * To run a query within a React component, call `useSearchQueryQuery` and pass it any options that fit your needs.
 * When your component renders, `useSearchQueryQuery` returns an object from Apollo Client that contains loading, error, and data properties
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = useSearchQueryQuery({
 *   variables: {
 *      query: // value for 'query'
 *      types: // value for 'types'
 *      datasourceIds: // value for 'datasourceIds'
 *      page: // value for 'page'
 *      perPage: // value for 'perPage'
 *   },
 * });
 */
export function useSearchQueryQuery(baseOptions?: Apollo.QueryHookOptions<SearchQueryQuery, SearchQueryQueryVariables>) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useQuery<SearchQueryQuery, SearchQueryQueryVariables>(SearchQueryDocument, options);
      }
export function useSearchQueryLazyQuery(baseOptions?: Apollo.LazyQueryHookOptions<SearchQueryQuery, SearchQueryQueryVariables>) {
          const options = {...defaultOptions, ...baseOptions}
          return Apollo.useLazyQuery<SearchQueryQuery, SearchQueryQueryVariables>(SearchQueryDocument, options);
        }
export type SearchQueryQueryHookResult = ReturnType<typeof useSearchQueryQuery>;
export type SearchQueryLazyQueryHookResult = ReturnType<typeof useSearchQueryLazyQuery>;
export type SearchQueryQueryResult = Apollo.QueryResult<SearchQueryQuery, SearchQueryQueryVariables>;
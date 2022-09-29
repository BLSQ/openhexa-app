import * as Types from '../../graphql-types';

import { gql } from '@apollo/client';
import * as Apollo from '@apollo/client';
const defaultOptions = {} as const;
export type DatasourcePickerQueryVariables = Types.Exact<{ [key: string]: never; }>;


export type DatasourcePickerQuery = { __typename?: 'Query', catalog: { __typename?: 'CatalogPage', items: Array<{ __typename?: 'CatalogEntry', id: string, objectId: string, name: string, symbol?: any | null, type: { __typename?: 'CatalogEntryType', name: string, app: string } }> } };


export const DatasourcePickerDocument = gql`
    query DatasourcePicker {
  catalog(page: 1, perPage: 25) {
    items {
      id
      objectId
      name
      symbol
      type {
        name
        app
      }
    }
  }
}
    `;

/**
 * __useDatasourcePickerQuery__
 *
 * To run a query within a React component, call `useDatasourcePickerQuery` and pass it any options that fit your needs.
 * When your component renders, `useDatasourcePickerQuery` returns an object from Apollo Client that contains loading, error, and data properties
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = useDatasourcePickerQuery({
 *   variables: {
 *   },
 * });
 */
export function useDatasourcePickerQuery(baseOptions?: Apollo.QueryHookOptions<DatasourcePickerQuery, DatasourcePickerQueryVariables>) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useQuery<DatasourcePickerQuery, DatasourcePickerQueryVariables>(DatasourcePickerDocument, options);
      }
export function useDatasourcePickerLazyQuery(baseOptions?: Apollo.LazyQueryHookOptions<DatasourcePickerQuery, DatasourcePickerQueryVariables>) {
          const options = {...defaultOptions, ...baseOptions}
          return Apollo.useLazyQuery<DatasourcePickerQuery, DatasourcePickerQueryVariables>(DatasourcePickerDocument, options);
        }
export type DatasourcePickerQueryHookResult = ReturnType<typeof useDatasourcePickerQuery>;
export type DatasourcePickerLazyQueryHookResult = ReturnType<typeof useDatasourcePickerLazyQuery>;
export type DatasourcePickerQueryResult = Apollo.QueryResult<DatasourcePickerQuery, DatasourcePickerQueryVariables>;
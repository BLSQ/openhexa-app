import * as Types from '../../graphql/types';

import { gql } from '@apollo/client';
import * as Apollo from '@apollo/client';
const defaultOptions = {} as const;
export type NotebooksPageQueryVariables = Types.Exact<{ [key: string]: never; }>;


export type NotebooksPageQuery = { __typename?: 'Query', notebooksUrl: any };


export const NotebooksPageDocument = gql`
    query notebooksPage {
  notebooksUrl
}
    `;

/**
 * __useNotebooksPageQuery__
 *
 * To run a query within a React component, call `useNotebooksPageQuery` and pass it any options that fit your needs.
 * When your component renders, `useNotebooksPageQuery` returns an object from Apollo Client that contains loading, error, and data properties
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = useNotebooksPageQuery({
 *   variables: {
 *   },
 * });
 */
export function useNotebooksPageQuery(baseOptions?: Apollo.QueryHookOptions<NotebooksPageQuery, NotebooksPageQueryVariables>) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useQuery<NotebooksPageQuery, NotebooksPageQueryVariables>(NotebooksPageDocument, options);
      }
export function useNotebooksPageLazyQuery(baseOptions?: Apollo.LazyQueryHookOptions<NotebooksPageQuery, NotebooksPageQueryVariables>) {
          const options = {...defaultOptions, ...baseOptions}
          return Apollo.useLazyQuery<NotebooksPageQuery, NotebooksPageQueryVariables>(NotebooksPageDocument, options);
        }
export function useNotebooksPageSuspenseQuery(baseOptions?: Apollo.SkipToken | Apollo.SuspenseQueryHookOptions<NotebooksPageQuery, NotebooksPageQueryVariables>) {
          const options = baseOptions === Apollo.skipToken ? baseOptions : {...defaultOptions, ...baseOptions}
          return Apollo.useSuspenseQuery<NotebooksPageQuery, NotebooksPageQueryVariables>(NotebooksPageDocument, options);
        }
export type NotebooksPageQueryHookResult = ReturnType<typeof useNotebooksPageQuery>;
export type NotebooksPageLazyQueryHookResult = ReturnType<typeof useNotebooksPageLazyQuery>;
export type NotebooksPageSuspenseQueryHookResult = ReturnType<typeof useNotebooksPageSuspenseQuery>;
export type NotebooksPageQueryResult = Apollo.QueryResult<NotebooksPageQuery, NotebooksPageQueryVariables>;
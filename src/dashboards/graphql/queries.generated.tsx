import * as Types from '../../graphql-types';

import { gql } from '@apollo/client';
import * as Apollo from '@apollo/client';
const defaultOptions = {} as const;
export type DashboardPageQueryVariables = Types.Exact<{ [key: string]: never; }>;


export type DashboardPageQuery = { __typename?: 'Query', totalNotebooks: number, catalog: { __typename?: 'CatalogPage', totalItems: number }, dags: { __typename?: 'DAGPage', totalItems: number }, lastActivities: Array<{ __typename?: 'Activity', description: string, occurredAt: any, url: any, status: Types.ActivityStatus }> };


export const DashboardPageDocument = gql`
    query DashboardPage {
  totalNotebooks
  catalog {
    totalItems
  }
  dags {
    totalItems
  }
  lastActivities {
    description
    occurredAt
    url
    status
  }
}
    `;

/**
 * __useDashboardPageQuery__
 *
 * To run a query within a React component, call `useDashboardPageQuery` and pass it any options that fit your needs.
 * When your component renders, `useDashboardPageQuery` returns an object from Apollo Client that contains loading, error, and data properties
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = useDashboardPageQuery({
 *   variables: {
 *   },
 * });
 */
export function useDashboardPageQuery(baseOptions?: Apollo.QueryHookOptions<DashboardPageQuery, DashboardPageQueryVariables>) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useQuery<DashboardPageQuery, DashboardPageQueryVariables>(DashboardPageDocument, options);
      }
export function useDashboardPageLazyQuery(baseOptions?: Apollo.LazyQueryHookOptions<DashboardPageQuery, DashboardPageQueryVariables>) {
          const options = {...defaultOptions, ...baseOptions}
          return Apollo.useLazyQuery<DashboardPageQuery, DashboardPageQueryVariables>(DashboardPageDocument, options);
        }
export function useDashboardPageSuspenseQuery(baseOptions?: Apollo.SuspenseQueryHookOptions<DashboardPageQuery, DashboardPageQueryVariables>) {
          const options = {...defaultOptions, ...baseOptions}
          return Apollo.useSuspenseQuery<DashboardPageQuery, DashboardPageQueryVariables>(DashboardPageDocument, options);
        }
export type DashboardPageQueryHookResult = ReturnType<typeof useDashboardPageQuery>;
export type DashboardPageLazyQueryHookResult = ReturnType<typeof useDashboardPageLazyQuery>;
export type DashboardPageSuspenseQueryHookResult = ReturnType<typeof useDashboardPageSuspenseQuery>;
export type DashboardPageQueryResult = Apollo.QueryResult<DashboardPageQuery, DashboardPageQueryVariables>;
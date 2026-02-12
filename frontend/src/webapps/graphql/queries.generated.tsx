import * as Types from '../../graphql/types';

import { gql } from '@apollo/client';
import * as Apollo from '@apollo/client';
const defaultOptions = {} as const;
export type SupersetInstancesQueryVariables = Types.Exact<{
  workspaceSlug: Types.Scalars['String']['input'];
}>;


export type SupersetInstancesQuery = { __typename?: 'Query', supersetInstances: Array<{ __typename?: 'SupersetInstance', id: string, name: string }> };


export const SupersetInstancesDocument = gql`
    query SupersetInstances($workspaceSlug: String!) {
  supersetInstances(workspaceSlug: $workspaceSlug) {
    id
    name
  }
}
    `;

/**
 * __useSupersetInstancesQuery__
 *
 * To run a query within a React component, call `useSupersetInstancesQuery` and pass it any options that fit your needs.
 * When your component renders, `useSupersetInstancesQuery` returns an object from Apollo Client that contains loading, error, and data properties
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = useSupersetInstancesQuery({
 *   variables: {
 *      workspaceSlug: // value for 'workspaceSlug'
 *   },
 * });
 */
export function useSupersetInstancesQuery(baseOptions: Apollo.QueryHookOptions<SupersetInstancesQuery, SupersetInstancesQueryVariables> & ({ variables: SupersetInstancesQueryVariables; skip?: boolean; } | { skip: boolean; }) ) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useQuery<SupersetInstancesQuery, SupersetInstancesQueryVariables>(SupersetInstancesDocument, options);
      }
export function useSupersetInstancesLazyQuery(baseOptions?: Apollo.LazyQueryHookOptions<SupersetInstancesQuery, SupersetInstancesQueryVariables>) {
          const options = {...defaultOptions, ...baseOptions}
          return Apollo.useLazyQuery<SupersetInstancesQuery, SupersetInstancesQueryVariables>(SupersetInstancesDocument, options);
        }
export function useSupersetInstancesSuspenseQuery(baseOptions?: Apollo.SkipToken | Apollo.SuspenseQueryHookOptions<SupersetInstancesQuery, SupersetInstancesQueryVariables>) {
          const options = baseOptions === Apollo.skipToken ? baseOptions : {...defaultOptions, ...baseOptions}
          return Apollo.useSuspenseQuery<SupersetInstancesQuery, SupersetInstancesQueryVariables>(SupersetInstancesDocument, options);
        }
export type SupersetInstancesQueryHookResult = ReturnType<typeof useSupersetInstancesQuery>;
export type SupersetInstancesLazyQueryHookResult = ReturnType<typeof useSupersetInstancesLazyQuery>;
export type SupersetInstancesSuspenseQueryHookResult = ReturnType<typeof useSupersetInstancesSuspenseQuery>;
export type SupersetInstancesQueryResult = Apollo.QueryResult<SupersetInstancesQuery, SupersetInstancesQueryVariables>;
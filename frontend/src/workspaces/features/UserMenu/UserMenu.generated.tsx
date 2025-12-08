import * as Types from '../../../graphql/types';

import { gql } from '@apollo/client';
import * as Apollo from '@apollo/client';
const defaultOptions = {} as const;
export type UserMenuQueryVariables = Types.Exact<{ [key: string]: never; }>;


export type UserMenuQuery = { __typename?: 'Query', pendingWorkspaceInvitations: { __typename?: 'WorkspaceInvitationPage', totalItems: number } };


export const UserMenuDocument = gql`
    query UserMenu {
  pendingWorkspaceInvitations(page: 1, perPage: 1) {
    totalItems
  }
}
    `;

/**
 * __useUserMenuQuery__
 *
 * To run a query within a React component, call `useUserMenuQuery` and pass it any options that fit your needs.
 * When your component renders, `useUserMenuQuery` returns an object from Apollo Client that contains loading, error, and data properties
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = useUserMenuQuery({
 *   variables: {
 *   },
 * });
 */
export function useUserMenuQuery(baseOptions?: Apollo.QueryHookOptions<UserMenuQuery, UserMenuQueryVariables>) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useQuery<UserMenuQuery, UserMenuQueryVariables>(UserMenuDocument, options);
      }
export function useUserMenuLazyQuery(baseOptions?: Apollo.LazyQueryHookOptions<UserMenuQuery, UserMenuQueryVariables>) {
          const options = {...defaultOptions, ...baseOptions}
          return Apollo.useLazyQuery<UserMenuQuery, UserMenuQueryVariables>(UserMenuDocument, options);
        }
export function useUserMenuSuspenseQuery(baseOptions?: Apollo.SkipToken | Apollo.SuspenseQueryHookOptions<UserMenuQuery, UserMenuQueryVariables>) {
          const options = baseOptions === Apollo.skipToken ? baseOptions : {...defaultOptions, ...baseOptions}
          return Apollo.useSuspenseQuery<UserMenuQuery, UserMenuQueryVariables>(UserMenuDocument, options);
        }
export type UserMenuQueryHookResult = ReturnType<typeof useUserMenuQuery>;
export type UserMenuLazyQueryHookResult = ReturnType<typeof useUserMenuLazyQuery>;
export type UserMenuSuspenseQueryHookResult = ReturnType<typeof useUserMenuSuspenseQuery>;
export type UserMenuQueryResult = Apollo.QueryResult<UserMenuQuery, UserMenuQueryVariables>;
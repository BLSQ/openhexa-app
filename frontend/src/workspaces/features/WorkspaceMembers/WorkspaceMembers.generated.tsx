import * as Types from '../../../graphql/types';

import { gql } from '@apollo/client';
import * as Apollo from '@apollo/client';
const defaultOptions = {} as const;
export type WorskspaceMembersQueryVariables = Types.Exact<{
  slug: Types.Scalars['String']['input'];
  page?: Types.InputMaybe<Types.Scalars['Int']['input']>;
  perPage?: Types.InputMaybe<Types.Scalars['Int']['input']>;
}>;


export type WorskspaceMembersQuery = { __typename?: 'Query', workspace?: { __typename?: 'Workspace', slug: string, permissions: { __typename?: 'WorkspacePermissions', manageMembers: boolean }, members: { __typename?: 'WorkspaceMembershipPage', totalItems: number, items: Array<{ __typename?: 'WorkspaceMembership', id: string, role: Types.WorkspaceMembershipRole, createdAt: any, user: { __typename?: 'User', id: string, displayName: string, email: string } }> } } | null };


export const WorskspaceMembersDocument = gql`
    query WorskspaceMembers($slug: String!, $page: Int, $perPage: Int) {
  workspace(slug: $slug) {
    slug
    permissions {
      manageMembers
    }
    members(page: $page, perPage: $perPage) {
      totalItems
      items {
        id
        role
        user {
          id
          displayName
          email
        }
        createdAt
      }
    }
  }
}
    `;

/**
 * __useWorskspaceMembersQuery__
 *
 * To run a query within a React component, call `useWorskspaceMembersQuery` and pass it any options that fit your needs.
 * When your component renders, `useWorskspaceMembersQuery` returns an object from Apollo Client that contains loading, error, and data properties
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = useWorskspaceMembersQuery({
 *   variables: {
 *      slug: // value for 'slug'
 *      page: // value for 'page'
 *      perPage: // value for 'perPage'
 *   },
 * });
 */
export function useWorskspaceMembersQuery(baseOptions: Apollo.QueryHookOptions<WorskspaceMembersQuery, WorskspaceMembersQueryVariables> & ({ variables: WorskspaceMembersQueryVariables; skip?: boolean; } | { skip: boolean; }) ) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useQuery<WorskspaceMembersQuery, WorskspaceMembersQueryVariables>(WorskspaceMembersDocument, options);
      }
export function useWorskspaceMembersLazyQuery(baseOptions?: Apollo.LazyQueryHookOptions<WorskspaceMembersQuery, WorskspaceMembersQueryVariables>) {
          const options = {...defaultOptions, ...baseOptions}
          return Apollo.useLazyQuery<WorskspaceMembersQuery, WorskspaceMembersQueryVariables>(WorskspaceMembersDocument, options);
        }
export function useWorskspaceMembersSuspenseQuery(baseOptions?: Apollo.SkipToken | Apollo.SuspenseQueryHookOptions<WorskspaceMembersQuery, WorskspaceMembersQueryVariables>) {
          const options = baseOptions === Apollo.skipToken ? baseOptions : {...defaultOptions, ...baseOptions}
          return Apollo.useSuspenseQuery<WorskspaceMembersQuery, WorskspaceMembersQueryVariables>(WorskspaceMembersDocument, options);
        }
export type WorskspaceMembersQueryHookResult = ReturnType<typeof useWorskspaceMembersQuery>;
export type WorskspaceMembersLazyQueryHookResult = ReturnType<typeof useWorskspaceMembersLazyQuery>;
export type WorskspaceMembersSuspenseQueryHookResult = ReturnType<typeof useWorskspaceMembersSuspenseQuery>;
export type WorskspaceMembersQueryResult = Apollo.QueryResult<WorskspaceMembersQuery, WorskspaceMembersQueryVariables>;
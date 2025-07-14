import * as Types from '../../../graphql/types';

import { gql } from '@apollo/client';
import * as Apollo from '@apollo/client';
const defaultOptions = {} as const;
export type OrganizationMembersQueryVariables = Types.Exact<{
  id: Types.Scalars['UUID']['input'];
  page?: Types.InputMaybe<Types.Scalars['Int']['input']>;
  perPage?: Types.InputMaybe<Types.Scalars['Int']['input']>;
  term?: Types.InputMaybe<Types.Scalars['String']['input']>;
}>;


export type OrganizationMembersQuery = { __typename?: 'Query', organization?: { __typename?: 'Organization', id: string, permissions: { __typename?: 'OrganizationPermissions', manageMembers: boolean }, members: { __typename?: 'OrganizationMembershipPage', totalItems: number, items: Array<{ __typename?: 'OrganizationMembership', id: string, role: Types.OrganizationMembershipRole, createdAt: any, workspaceMemberships: Array<{ __typename?: 'WorkspaceMembership', id: string, workspace: { __typename?: 'Workspace', name: string } }>, user: { __typename?: 'User', id: string, displayName: string, email: string } }> } } | null };


export const OrganizationMembersDocument = gql`
    query OrganizationMembers($id: UUID!, $page: Int, $perPage: Int, $term: String) {
  organization(id: $id) {
    id
    permissions {
      manageMembers
    }
    members(page: $page, perPage: $perPage, term: $term) {
      totalItems
      items {
        id
        role
        workspaceMemberships {
          id
          workspace {
            name
          }
        }
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
 * __useOrganizationMembersQuery__
 *
 * To run a query within a React component, call `useOrganizationMembersQuery` and pass it any options that fit your needs.
 * When your component renders, `useOrganizationMembersQuery` returns an object from Apollo Client that contains loading, error, and data properties
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = useOrganizationMembersQuery({
 *   variables: {
 *      id: // value for 'id'
 *      page: // value for 'page'
 *      perPage: // value for 'perPage'
 *      term: // value for 'term'
 *   },
 * });
 */
export function useOrganizationMembersQuery(baseOptions: Apollo.QueryHookOptions<OrganizationMembersQuery, OrganizationMembersQueryVariables> & ({ variables: OrganizationMembersQueryVariables; skip?: boolean; } | { skip: boolean; }) ) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useQuery<OrganizationMembersQuery, OrganizationMembersQueryVariables>(OrganizationMembersDocument, options);
      }
export function useOrganizationMembersLazyQuery(baseOptions?: Apollo.LazyQueryHookOptions<OrganizationMembersQuery, OrganizationMembersQueryVariables>) {
          const options = {...defaultOptions, ...baseOptions}
          return Apollo.useLazyQuery<OrganizationMembersQuery, OrganizationMembersQueryVariables>(OrganizationMembersDocument, options);
        }
export function useOrganizationMembersSuspenseQuery(baseOptions?: Apollo.SkipToken | Apollo.SuspenseQueryHookOptions<OrganizationMembersQuery, OrganizationMembersQueryVariables>) {
          const options = baseOptions === Apollo.skipToken ? baseOptions : {...defaultOptions, ...baseOptions}
          return Apollo.useSuspenseQuery<OrganizationMembersQuery, OrganizationMembersQueryVariables>(OrganizationMembersDocument, options);
        }
export type OrganizationMembersQueryHookResult = ReturnType<typeof useOrganizationMembersQuery>;
export type OrganizationMembersLazyQueryHookResult = ReturnType<typeof useOrganizationMembersLazyQuery>;
export type OrganizationMembersSuspenseQueryHookResult = ReturnType<typeof useOrganizationMembersSuspenseQuery>;
export type OrganizationMembersQueryResult = Apollo.QueryResult<OrganizationMembersQuery, OrganizationMembersQueryVariables>;
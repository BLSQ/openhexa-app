import * as Types from '../../../graphql/types';

import { gql } from '@apollo/client';
import * as Apollo from '@apollo/client';
const defaultOptions = {} as const;
export type WorskspaceInvitationsQueryVariables = Types.Exact<{
  slug: Types.Scalars['String']['input'];
  page?: Types.InputMaybe<Types.Scalars['Int']['input']>;
  perPage?: Types.InputMaybe<Types.Scalars['Int']['input']>;
}>;


export type WorskspaceInvitationsQuery = { __typename?: 'Query', workspace?: { __typename?: 'Workspace', slug: string, permissions: { __typename?: 'WorkspacePermissions', manageMembers: boolean }, invitations: { __typename?: 'WorkspaceInvitationPage', totalItems: number, items: Array<{ __typename?: 'WorkspaceInvitation', id: string, role: Types.WorkspaceMembershipRole, email: string, status: Types.WorkspaceInvitationStatus, createdAt: any, invitedBy?: { __typename?: 'User', displayName: string } | null }> } } | null };


export const WorskspaceInvitationsDocument = gql`
    query WorskspaceInvitations($slug: String!, $page: Int, $perPage: Int) {
  workspace(slug: $slug) {
    slug
    permissions {
      manageMembers
    }
    invitations(page: $page, perPage: $perPage) {
      totalItems
      items {
        id
        role
        email
        status
        invitedBy {
          displayName
        }
        createdAt
      }
    }
  }
}
    `;

/**
 * __useWorskspaceInvitationsQuery__
 *
 * To run a query within a React component, call `useWorskspaceInvitationsQuery` and pass it any options that fit your needs.
 * When your component renders, `useWorskspaceInvitationsQuery` returns an object from Apollo Client that contains loading, error, and data properties
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = useWorskspaceInvitationsQuery({
 *   variables: {
 *      slug: // value for 'slug'
 *      page: // value for 'page'
 *      perPage: // value for 'perPage'
 *   },
 * });
 */
export function useWorskspaceInvitationsQuery(baseOptions: Apollo.QueryHookOptions<WorskspaceInvitationsQuery, WorskspaceInvitationsQueryVariables> & ({ variables: WorskspaceInvitationsQueryVariables; skip?: boolean; } | { skip: boolean; }) ) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useQuery<WorskspaceInvitationsQuery, WorskspaceInvitationsQueryVariables>(WorskspaceInvitationsDocument, options);
      }
export function useWorskspaceInvitationsLazyQuery(baseOptions?: Apollo.LazyQueryHookOptions<WorskspaceInvitationsQuery, WorskspaceInvitationsQueryVariables>) {
          const options = {...defaultOptions, ...baseOptions}
          return Apollo.useLazyQuery<WorskspaceInvitationsQuery, WorskspaceInvitationsQueryVariables>(WorskspaceInvitationsDocument, options);
        }
export function useWorskspaceInvitationsSuspenseQuery(baseOptions?: Apollo.SkipToken | Apollo.SuspenseQueryHookOptions<WorskspaceInvitationsQuery, WorskspaceInvitationsQueryVariables>) {
          const options = baseOptions === Apollo.skipToken ? baseOptions : {...defaultOptions, ...baseOptions}
          return Apollo.useSuspenseQuery<WorskspaceInvitationsQuery, WorskspaceInvitationsQueryVariables>(WorskspaceInvitationsDocument, options);
        }
export type WorskspaceInvitationsQueryHookResult = ReturnType<typeof useWorskspaceInvitationsQuery>;
export type WorskspaceInvitationsLazyQueryHookResult = ReturnType<typeof useWorskspaceInvitationsLazyQuery>;
export type WorskspaceInvitationsSuspenseQueryHookResult = ReturnType<typeof useWorskspaceInvitationsSuspenseQuery>;
export type WorskspaceInvitationsQueryResult = Apollo.QueryResult<WorskspaceInvitationsQuery, WorskspaceInvitationsQueryVariables>;
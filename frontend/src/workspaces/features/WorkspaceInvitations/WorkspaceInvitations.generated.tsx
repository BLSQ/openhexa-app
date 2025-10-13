import * as Types from '../../../graphql/types';

import { gql } from '@apollo/client';
import * as Apollo from '@apollo/client';
const defaultOptions = {} as const;
export type WorkspaceInvitationsQueryVariables = Types.Exact<{
  slug: Types.Scalars['String']['input'];
  page?: Types.InputMaybe<Types.Scalars['Int']['input']>;
  perPage?: Types.InputMaybe<Types.Scalars['Int']['input']>;
}>;


export type WorkspaceInvitationsQuery = { __typename?: 'Query', workspace?: { __typename?: 'Workspace', slug: string, permissions: { __typename?: 'WorkspacePermissions', manageMembers: boolean }, invitations: { __typename?: 'WorkspaceInvitationPage', totalItems: number, items: Array<{ __typename?: 'WorkspaceInvitation', id: string, role: Types.WorkspaceMembershipRole, email: string, status: Types.WorkspaceInvitationStatus, createdAt: any, invitedBy?: { __typename?: 'User', displayName: string } | null }> } } | null };


export const WorkspaceInvitationsDocument = gql`
    query WorkspaceInvitations($slug: String!, $page: Int, $perPage: Int) {
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
 * __useWorkspaceInvitationsQuery__
 *
 * To run a query within a React component, call `useWorkspaceInvitationsQuery` and pass it any options that fit your needs.
 * When your component renders, `useWorkspaceInvitationsQuery` returns an object from Apollo Client that contains loading, error, and data properties
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = useWorkspaceInvitationsQuery({
 *   variables: {
 *      slug: // value for 'slug'
 *      page: // value for 'page'
 *      perPage: // value for 'perPage'
 *   },
 * });
 */
export function useWorkspaceInvitationsQuery(baseOptions: Apollo.QueryHookOptions<WorkspaceInvitationsQuery, WorkspaceInvitationsQueryVariables> & ({ variables: WorkspaceInvitationsQueryVariables; skip?: boolean; } | { skip: boolean; }) ) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useQuery<WorkspaceInvitationsQuery, WorkspaceInvitationsQueryVariables>(WorkspaceInvitationsDocument, options);
      }
export function useWorkspaceInvitationsLazyQuery(baseOptions?: Apollo.LazyQueryHookOptions<WorkspaceInvitationsQuery, WorkspaceInvitationsQueryVariables>) {
          const options = {...defaultOptions, ...baseOptions}
          return Apollo.useLazyQuery<WorkspaceInvitationsQuery, WorkspaceInvitationsQueryVariables>(WorkspaceInvitationsDocument, options);
        }
export function useWorkspaceInvitationsSuspenseQuery(baseOptions?: Apollo.SkipToken | Apollo.SuspenseQueryHookOptions<WorkspaceInvitationsQuery, WorkspaceInvitationsQueryVariables>) {
          const options = baseOptions === Apollo.skipToken ? baseOptions : {...defaultOptions, ...baseOptions}
          return Apollo.useSuspenseQuery<WorkspaceInvitationsQuery, WorkspaceInvitationsQueryVariables>(WorkspaceInvitationsDocument, options);
        }
export type WorkspaceInvitationsQueryHookResult = ReturnType<typeof useWorkspaceInvitationsQuery>;
export type WorkspaceInvitationsLazyQueryHookResult = ReturnType<typeof useWorkspaceInvitationsLazyQuery>;
export type WorkspaceInvitationsSuspenseQueryHookResult = ReturnType<typeof useWorkspaceInvitationsSuspenseQuery>;
export type WorkspaceInvitationsQueryResult = Apollo.QueryResult<WorkspaceInvitationsQuery, WorkspaceInvitationsQueryVariables>;
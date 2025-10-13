import * as Types from '../../../graphql/types';

import { gql } from '@apollo/client';
import * as Apollo from '@apollo/client';
const defaultOptions = {} as const;
export type OrganizationWorkspaceInvitationsQueryVariables = Types.Exact<{
  id: Types.Scalars['UUID']['input'];
  page?: Types.InputMaybe<Types.Scalars['Int']['input']>;
  perPage?: Types.InputMaybe<Types.Scalars['Int']['input']>;
}>;


export type OrganizationWorkspaceInvitationsQuery = { __typename?: 'Query', organization?: { __typename?: 'Organization', id: string, permissions: { __typename?: 'OrganizationPermissions', manageMembers: boolean }, pendingWorkspaceInvitations: { __typename?: 'WorkspaceInvitationPage', totalItems: number, items: Array<{ __typename?: 'WorkspaceInvitation', id: string, email: string, role: Types.WorkspaceMembershipRole, status: Types.WorkspaceInvitationStatus, createdAt: any, workspace: { __typename?: 'Workspace', name: string, slug: string }, invitedBy?: { __typename?: 'User', displayName: string } | null }> } } | null };

export type DeleteWorkspaceInvitationMutationVariables = Types.Exact<{
  input: Types.DeleteWorkspaceInvitationInput;
}>;


export type DeleteWorkspaceInvitationMutation = { __typename?: 'Mutation', deleteWorkspaceInvitation: { __typename?: 'DeleteWorkspaceInvitationResult', success: boolean, errors: Array<Types.DeleteWorkspaceInvitationError> } };

export type ResendWorkspaceInvitationMutationVariables = Types.Exact<{
  input: Types.ResendWorkspaceInvitationInput;
}>;


export type ResendWorkspaceInvitationMutation = { __typename?: 'Mutation', resendWorkspaceInvitation: { __typename?: 'ResendWorkspaceInvitationResult', success: boolean, errors: Array<Types.ResendWorkspaceInvitationError> } };


export const OrganizationWorkspaceInvitationsDocument = gql`
    query OrganizationWorkspaceInvitations($id: UUID!, $page: Int, $perPage: Int) {
  organization(id: $id) {
    id
    permissions {
      manageMembers
    }
    pendingWorkspaceInvitations(page: $page, perPage: $perPage) {
      totalItems
      items {
        id
        email
        role
        status
        workspace {
          name
          slug
        }
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
 * __useOrganizationWorkspaceInvitationsQuery__
 *
 * To run a query within a React component, call `useOrganizationWorkspaceInvitationsQuery` and pass it any options that fit your needs.
 * When your component renders, `useOrganizationWorkspaceInvitationsQuery` returns an object from Apollo Client that contains loading, error, and data properties
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = useOrganizationWorkspaceInvitationsQuery({
 *   variables: {
 *      id: // value for 'id'
 *      page: // value for 'page'
 *      perPage: // value for 'perPage'
 *   },
 * });
 */
export function useOrganizationWorkspaceInvitationsQuery(baseOptions: Apollo.QueryHookOptions<OrganizationWorkspaceInvitationsQuery, OrganizationWorkspaceInvitationsQueryVariables> & ({ variables: OrganizationWorkspaceInvitationsQueryVariables; skip?: boolean; } | { skip: boolean; }) ) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useQuery<OrganizationWorkspaceInvitationsQuery, OrganizationWorkspaceInvitationsQueryVariables>(OrganizationWorkspaceInvitationsDocument, options);
      }
export function useOrganizationWorkspaceInvitationsLazyQuery(baseOptions?: Apollo.LazyQueryHookOptions<OrganizationWorkspaceInvitationsQuery, OrganizationWorkspaceInvitationsQueryVariables>) {
          const options = {...defaultOptions, ...baseOptions}
          return Apollo.useLazyQuery<OrganizationWorkspaceInvitationsQuery, OrganizationWorkspaceInvitationsQueryVariables>(OrganizationWorkspaceInvitationsDocument, options);
        }
export function useOrganizationWorkspaceInvitationsSuspenseQuery(baseOptions?: Apollo.SkipToken | Apollo.SuspenseQueryHookOptions<OrganizationWorkspaceInvitationsQuery, OrganizationWorkspaceInvitationsQueryVariables>) {
          const options = baseOptions === Apollo.skipToken ? baseOptions : {...defaultOptions, ...baseOptions}
          return Apollo.useSuspenseQuery<OrganizationWorkspaceInvitationsQuery, OrganizationWorkspaceInvitationsQueryVariables>(OrganizationWorkspaceInvitationsDocument, options);
        }
export type OrganizationWorkspaceInvitationsQueryHookResult = ReturnType<typeof useOrganizationWorkspaceInvitationsQuery>;
export type OrganizationWorkspaceInvitationsLazyQueryHookResult = ReturnType<typeof useOrganizationWorkspaceInvitationsLazyQuery>;
export type OrganizationWorkspaceInvitationsSuspenseQueryHookResult = ReturnType<typeof useOrganizationWorkspaceInvitationsSuspenseQuery>;
export type OrganizationWorkspaceInvitationsQueryResult = Apollo.QueryResult<OrganizationWorkspaceInvitationsQuery, OrganizationWorkspaceInvitationsQueryVariables>;
export const DeleteWorkspaceInvitationDocument = gql`
    mutation DeleteWorkspaceInvitation($input: DeleteWorkspaceInvitationInput!) {
  deleteWorkspaceInvitation(input: $input) {
    success
    errors
  }
}
    `;
export type DeleteWorkspaceInvitationMutationFn = Apollo.MutationFunction<DeleteWorkspaceInvitationMutation, DeleteWorkspaceInvitationMutationVariables>;

/**
 * __useDeleteWorkspaceInvitationMutation__
 *
 * To run a mutation, you first call `useDeleteWorkspaceInvitationMutation` within a React component and pass it any options that fit your needs.
 * When your component renders, `useDeleteWorkspaceInvitationMutation` returns a tuple that includes:
 * - A mutate function that you can call at any time to execute the mutation
 * - An object with fields that represent the current status of the mutation's execution
 *
 * @param baseOptions options that will be passed into the mutation, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options-2;
 *
 * @example
 * const [deleteWorkspaceInvitationMutation, { data, loading, error }] = useDeleteWorkspaceInvitationMutation({
 *   variables: {
 *      input: // value for 'input'
 *   },
 * });
 */
export function useDeleteWorkspaceInvitationMutation(baseOptions?: Apollo.MutationHookOptions<DeleteWorkspaceInvitationMutation, DeleteWorkspaceInvitationMutationVariables>) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useMutation<DeleteWorkspaceInvitationMutation, DeleteWorkspaceInvitationMutationVariables>(DeleteWorkspaceInvitationDocument, options);
      }
export type DeleteWorkspaceInvitationMutationHookResult = ReturnType<typeof useDeleteWorkspaceInvitationMutation>;
export type DeleteWorkspaceInvitationMutationResult = Apollo.MutationResult<DeleteWorkspaceInvitationMutation>;
export type DeleteWorkspaceInvitationMutationOptions = Apollo.BaseMutationOptions<DeleteWorkspaceInvitationMutation, DeleteWorkspaceInvitationMutationVariables>;
export const ResendWorkspaceInvitationDocument = gql`
    mutation ResendWorkspaceInvitation($input: ResendWorkspaceInvitationInput!) {
  resendWorkspaceInvitation(input: $input) {
    success
    errors
  }
}
    `;
export type ResendWorkspaceInvitationMutationFn = Apollo.MutationFunction<ResendWorkspaceInvitationMutation, ResendWorkspaceInvitationMutationVariables>;

/**
 * __useResendWorkspaceInvitationMutation__
 *
 * To run a mutation, you first call `useResendWorkspaceInvitationMutation` within a React component and pass it any options that fit your needs.
 * When your component renders, `useResendWorkspaceInvitationMutation` returns a tuple that includes:
 * - A mutate function that you can call at any time to execute the mutation
 * - An object with fields that represent the current status of the mutation's execution
 *
 * @param baseOptions options that will be passed into the mutation, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options-2;
 *
 * @example
 * const [resendWorkspaceInvitationMutation, { data, loading, error }] = useResendWorkspaceInvitationMutation({
 *   variables: {
 *      input: // value for 'input'
 *   },
 * });
 */
export function useResendWorkspaceInvitationMutation(baseOptions?: Apollo.MutationHookOptions<ResendWorkspaceInvitationMutation, ResendWorkspaceInvitationMutationVariables>) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useMutation<ResendWorkspaceInvitationMutation, ResendWorkspaceInvitationMutationVariables>(ResendWorkspaceInvitationDocument, options);
      }
export type ResendWorkspaceInvitationMutationHookResult = ReturnType<typeof useResendWorkspaceInvitationMutation>;
export type ResendWorkspaceInvitationMutationResult = Apollo.MutationResult<ResendWorkspaceInvitationMutation>;
export type ResendWorkspaceInvitationMutationOptions = Apollo.BaseMutationOptions<ResendWorkspaceInvitationMutation, ResendWorkspaceInvitationMutationVariables>;
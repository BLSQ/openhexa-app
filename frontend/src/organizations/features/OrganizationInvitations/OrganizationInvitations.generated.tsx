import * as Types from '../../../graphql/types';

import { gql } from '@apollo/client';
import * as Apollo from '@apollo/client';
const defaultOptions = {} as const;
export type OrganizationInvitationsQueryVariables = Types.Exact<{
  id: Types.Scalars['UUID']['input'];
  page?: Types.InputMaybe<Types.Scalars['Int']['input']>;
  perPage?: Types.InputMaybe<Types.Scalars['Int']['input']>;
}>;


export type OrganizationInvitationsQuery = { __typename?: 'Query', organization?: { __typename?: 'Organization', id: string, permissions: { __typename?: 'OrganizationPermissions', manageMembers: boolean }, invitations: { __typename?: 'OrganizationInvitationPage', totalItems: number, items: Array<{ __typename?: 'OrganizationInvitation', id: string, role: Types.OrganizationMembershipRole, email: string, status: Types.OrganizationInvitationStatus, createdAt: any, invitedBy?: { __typename?: 'User', displayName: string } | null, workspaceInvitations: Array<{ __typename?: 'OrganizationWorkspaceInvitation', workspaceSlug: string, workspaceName: string, role: Types.WorkspaceMembershipRole }> }> } } | null };

export type DeleteOrganizationInvitationMutationVariables = Types.Exact<{
  input: Types.DeleteOrganizationInvitationInput;
}>;


export type DeleteOrganizationInvitationMutation = { __typename?: 'Mutation', deleteOrganizationInvitation: { __typename?: 'DeleteOrganizationInvitationResult', success: boolean, errors: Array<Types.DeleteOrganizationInvitationError> } };

export type ResendOrganizationInvitationMutationVariables = Types.Exact<{
  input: Types.ResendOrganizationInvitationInput;
}>;


export type ResendOrganizationInvitationMutation = { __typename?: 'Mutation', resendOrganizationInvitation: { __typename?: 'ResendOrganizationInvitationResult', success: boolean, errors: Array<Types.ResendOrganizationInvitationError> } };


export const OrganizationInvitationsDocument = gql`
    query OrganizationInvitations($id: UUID!, $page: Int, $perPage: Int) {
  organization(id: $id) {
    id
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
        workspaceInvitations {
          workspaceSlug
          workspaceName
          role
        }
      }
    }
  }
}
    `;

/**
 * __useOrganizationInvitationsQuery__
 *
 * To run a query within a React component, call `useOrganizationInvitationsQuery` and pass it any options that fit your needs.
 * When your component renders, `useOrganizationInvitationsQuery` returns an object from Apollo Client that contains loading, error, and data properties
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = useOrganizationInvitationsQuery({
 *   variables: {
 *      id: // value for 'id'
 *      page: // value for 'page'
 *      perPage: // value for 'perPage'
 *   },
 * });
 */
export function useOrganizationInvitationsQuery(baseOptions: Apollo.QueryHookOptions<OrganizationInvitationsQuery, OrganizationInvitationsQueryVariables> & ({ variables: OrganizationInvitationsQueryVariables; skip?: boolean; } | { skip: boolean; }) ) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useQuery<OrganizationInvitationsQuery, OrganizationInvitationsQueryVariables>(OrganizationInvitationsDocument, options);
      }
export function useOrganizationInvitationsLazyQuery(baseOptions?: Apollo.LazyQueryHookOptions<OrganizationInvitationsQuery, OrganizationInvitationsQueryVariables>) {
          const options = {...defaultOptions, ...baseOptions}
          return Apollo.useLazyQuery<OrganizationInvitationsQuery, OrganizationInvitationsQueryVariables>(OrganizationInvitationsDocument, options);
        }
export function useOrganizationInvitationsSuspenseQuery(baseOptions?: Apollo.SkipToken | Apollo.SuspenseQueryHookOptions<OrganizationInvitationsQuery, OrganizationInvitationsQueryVariables>) {
          const options = baseOptions === Apollo.skipToken ? baseOptions : {...defaultOptions, ...baseOptions}
          return Apollo.useSuspenseQuery<OrganizationInvitationsQuery, OrganizationInvitationsQueryVariables>(OrganizationInvitationsDocument, options);
        }
export type OrganizationInvitationsQueryHookResult = ReturnType<typeof useOrganizationInvitationsQuery>;
export type OrganizationInvitationsLazyQueryHookResult = ReturnType<typeof useOrganizationInvitationsLazyQuery>;
export type OrganizationInvitationsSuspenseQueryHookResult = ReturnType<typeof useOrganizationInvitationsSuspenseQuery>;
export type OrganizationInvitationsQueryResult = Apollo.QueryResult<OrganizationInvitationsQuery, OrganizationInvitationsQueryVariables>;
export const DeleteOrganizationInvitationDocument = gql`
    mutation DeleteOrganizationInvitation($input: DeleteOrganizationInvitationInput!) {
  deleteOrganizationInvitation(input: $input) {
    success
    errors
  }
}
    `;
export type DeleteOrganizationInvitationMutationFn = Apollo.MutationFunction<DeleteOrganizationInvitationMutation, DeleteOrganizationInvitationMutationVariables>;

/**
 * __useDeleteOrganizationInvitationMutation__
 *
 * To run a mutation, you first call `useDeleteOrganizationInvitationMutation` within a React component and pass it any options that fit your needs.
 * When your component renders, `useDeleteOrganizationInvitationMutation` returns a tuple that includes:
 * - A mutate function that you can call at any time to execute the mutation
 * - An object with fields that represent the current status of the mutation's execution
 *
 * @param baseOptions options that will be passed into the mutation, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options-2;
 *
 * @example
 * const [deleteOrganizationInvitationMutation, { data, loading, error }] = useDeleteOrganizationInvitationMutation({
 *   variables: {
 *      input: // value for 'input'
 *   },
 * });
 */
export function useDeleteOrganizationInvitationMutation(baseOptions?: Apollo.MutationHookOptions<DeleteOrganizationInvitationMutation, DeleteOrganizationInvitationMutationVariables>) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useMutation<DeleteOrganizationInvitationMutation, DeleteOrganizationInvitationMutationVariables>(DeleteOrganizationInvitationDocument, options);
      }
export type DeleteOrganizationInvitationMutationHookResult = ReturnType<typeof useDeleteOrganizationInvitationMutation>;
export type DeleteOrganizationInvitationMutationResult = Apollo.MutationResult<DeleteOrganizationInvitationMutation>;
export type DeleteOrganizationInvitationMutationOptions = Apollo.BaseMutationOptions<DeleteOrganizationInvitationMutation, DeleteOrganizationInvitationMutationVariables>;
export const ResendOrganizationInvitationDocument = gql`
    mutation ResendOrganizationInvitation($input: ResendOrganizationInvitationInput!) {
  resendOrganizationInvitation(input: $input) {
    success
    errors
  }
}
    `;
export type ResendOrganizationInvitationMutationFn = Apollo.MutationFunction<ResendOrganizationInvitationMutation, ResendOrganizationInvitationMutationVariables>;

/**
 * __useResendOrganizationInvitationMutation__
 *
 * To run a mutation, you first call `useResendOrganizationInvitationMutation` within a React component and pass it any options that fit your needs.
 * When your component renders, `useResendOrganizationInvitationMutation` returns a tuple that includes:
 * - A mutate function that you can call at any time to execute the mutation
 * - An object with fields that represent the current status of the mutation's execution
 *
 * @param baseOptions options that will be passed into the mutation, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options-2;
 *
 * @example
 * const [resendOrganizationInvitationMutation, { data, loading, error }] = useResendOrganizationInvitationMutation({
 *   variables: {
 *      input: // value for 'input'
 *   },
 * });
 */
export function useResendOrganizationInvitationMutation(baseOptions?: Apollo.MutationHookOptions<ResendOrganizationInvitationMutation, ResendOrganizationInvitationMutationVariables>) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useMutation<ResendOrganizationInvitationMutation, ResendOrganizationInvitationMutationVariables>(ResendOrganizationInvitationDocument, options);
      }
export type ResendOrganizationInvitationMutationHookResult = ReturnType<typeof useResendOrganizationInvitationMutation>;
export type ResendOrganizationInvitationMutationResult = Apollo.MutationResult<ResendOrganizationInvitationMutation>;
export type ResendOrganizationInvitationMutationOptions = Apollo.BaseMutationOptions<ResendOrganizationInvitationMutation, ResendOrganizationInvitationMutationVariables>;
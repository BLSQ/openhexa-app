import * as Types from '../../../graphql/types';

import { gql } from '@apollo/client';
import { WorkspaceRoleFragmentDoc } from '../../components/WorkspaceRolesList.generated';
import { User_UserFragmentDoc } from '../../../core/features/User/User.generated';
import * as Apollo from '@apollo/client';
const defaultOptions = {} as const;
export type OrganizationExternalCollaboratorsQueryVariables = Types.Exact<{
  id: Types.Scalars['UUID']['input'];
  page?: Types.InputMaybe<Types.Scalars['Int']['input']>;
  perPage?: Types.InputMaybe<Types.Scalars['Int']['input']>;
  term?: Types.InputMaybe<Types.Scalars['String']['input']>;
}>;


export type OrganizationExternalCollaboratorsQuery = { __typename?: 'Query', organization?: { __typename?: 'Organization', id: string, permissions: { __typename?: 'OrganizationPermissions', manageMembers: boolean, manageOwners: boolean }, workspaces: { __typename?: 'WorkspacePage', items: Array<{ __typename?: 'Workspace', slug: string, name: string }> }, externalCollaborators: { __typename?: 'ExternalCollaboratorPage', totalItems: number, items: Array<{ __typename?: 'ExternalCollaborator', id: string, createdAt: any, workspaceMemberships: Array<{ __typename?: 'WorkspaceMembership', id: string, role: Types.WorkspaceMembershipRole, workspace: { __typename?: 'Workspace', slug: string, name: string } }>, user: { __typename?: 'User', id: string, email: string, displayName: string, avatar: { __typename?: 'Avatar', initials: string, color: string } } }> } } | null };

export type UpdateExternalCollaboratorMutationVariables = Types.Exact<{
  input: Types.UpdateExternalCollaboratorInput;
}>;


export type UpdateExternalCollaboratorMutation = { __typename?: 'Mutation', updateExternalCollaborator: { __typename?: 'UpdateExternalCollaboratorResult', success: boolean, errors: Array<Types.UpdateExternalCollaboratorError> } };

export type DeleteExternalCollaboratorMutationVariables = Types.Exact<{
  input: Types.DeleteExternalCollaboratorInput;
}>;


export type DeleteExternalCollaboratorMutation = { __typename?: 'Mutation', deleteExternalCollaborator: { __typename?: 'DeleteExternalCollaboratorResult', success: boolean, errors: Array<Types.DeleteExternalCollaboratorError> } };

export type InviteOrganizationMemberMutationVariables = Types.Exact<{
  input: Types.InviteOrganizationMemberInput;
}>;


export type InviteOrganizationMemberMutation = { __typename?: 'Mutation', inviteOrganizationMember: { __typename?: 'InviteOrganizationMemberResult', success: boolean, errors: Array<Types.InviteOrganizationMemberError> } };


export const OrganizationExternalCollaboratorsDocument = gql`
    query OrganizationExternalCollaborators($id: UUID!, $page: Int, $perPage: Int, $term: String) {
  organization(id: $id) {
    id
    permissions {
      manageMembers
      manageOwners
    }
    workspaces(perPage: 1000, page: 1) {
      items {
        slug
        name
      }
    }
    externalCollaborators(page: $page, perPage: $perPage, term: $term) {
      totalItems
      items {
        id
        workspaceMemberships {
          ...WorkspaceRole
          id
          role
          workspace {
            slug
            name
          }
        }
        user {
          ...User_user
        }
        createdAt
      }
    }
  }
}
    ${WorkspaceRoleFragmentDoc}
${User_UserFragmentDoc}`;

/**
 * __useOrganizationExternalCollaboratorsQuery__
 *
 * To run a query within a React component, call `useOrganizationExternalCollaboratorsQuery` and pass it any options that fit your needs.
 * When your component renders, `useOrganizationExternalCollaboratorsQuery` returns an object from Apollo Client that contains loading, error, and data properties
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = useOrganizationExternalCollaboratorsQuery({
 *   variables: {
 *      id: // value for 'id'
 *      page: // value for 'page'
 *      perPage: // value for 'perPage'
 *      term: // value for 'term'
 *   },
 * });
 */
export function useOrganizationExternalCollaboratorsQuery(baseOptions: Apollo.QueryHookOptions<OrganizationExternalCollaboratorsQuery, OrganizationExternalCollaboratorsQueryVariables> & ({ variables: OrganizationExternalCollaboratorsQueryVariables; skip?: boolean; } | { skip: boolean; }) ) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useQuery<OrganizationExternalCollaboratorsQuery, OrganizationExternalCollaboratorsQueryVariables>(OrganizationExternalCollaboratorsDocument, options);
      }
export function useOrganizationExternalCollaboratorsLazyQuery(baseOptions?: Apollo.LazyQueryHookOptions<OrganizationExternalCollaboratorsQuery, OrganizationExternalCollaboratorsQueryVariables>) {
          const options = {...defaultOptions, ...baseOptions}
          return Apollo.useLazyQuery<OrganizationExternalCollaboratorsQuery, OrganizationExternalCollaboratorsQueryVariables>(OrganizationExternalCollaboratorsDocument, options);
        }
export function useOrganizationExternalCollaboratorsSuspenseQuery(baseOptions?: Apollo.SkipToken | Apollo.SuspenseQueryHookOptions<OrganizationExternalCollaboratorsQuery, OrganizationExternalCollaboratorsQueryVariables>) {
          const options = baseOptions === Apollo.skipToken ? baseOptions : {...defaultOptions, ...baseOptions}
          return Apollo.useSuspenseQuery<OrganizationExternalCollaboratorsQuery, OrganizationExternalCollaboratorsQueryVariables>(OrganizationExternalCollaboratorsDocument, options);
        }
export type OrganizationExternalCollaboratorsQueryHookResult = ReturnType<typeof useOrganizationExternalCollaboratorsQuery>;
export type OrganizationExternalCollaboratorsLazyQueryHookResult = ReturnType<typeof useOrganizationExternalCollaboratorsLazyQuery>;
export type OrganizationExternalCollaboratorsSuspenseQueryHookResult = ReturnType<typeof useOrganizationExternalCollaboratorsSuspenseQuery>;
export type OrganizationExternalCollaboratorsQueryResult = Apollo.QueryResult<OrganizationExternalCollaboratorsQuery, OrganizationExternalCollaboratorsQueryVariables>;
export const UpdateExternalCollaboratorDocument = gql`
    mutation UpdateExternalCollaborator($input: UpdateExternalCollaboratorInput!) {
  updateExternalCollaborator(input: $input) {
    success
    errors
  }
}
    `;
export type UpdateExternalCollaboratorMutationFn = Apollo.MutationFunction<UpdateExternalCollaboratorMutation, UpdateExternalCollaboratorMutationVariables>;

/**
 * __useUpdateExternalCollaboratorMutation__
 *
 * To run a mutation, you first call `useUpdateExternalCollaboratorMutation` within a React component and pass it any options that fit your needs.
 * When your component renders, `useUpdateExternalCollaboratorMutation` returns a tuple that includes:
 * - A mutate function that you can call at any time to execute the mutation
 * - An object with fields that represent the current status of the mutation's execution
 *
 * @param baseOptions options that will be passed into the mutation, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options-2;
 *
 * @example
 * const [updateExternalCollaboratorMutation, { data, loading, error }] = useUpdateExternalCollaboratorMutation({
 *   variables: {
 *      input: // value for 'input'
 *   },
 * });
 */
export function useUpdateExternalCollaboratorMutation(baseOptions?: Apollo.MutationHookOptions<UpdateExternalCollaboratorMutation, UpdateExternalCollaboratorMutationVariables>) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useMutation<UpdateExternalCollaboratorMutation, UpdateExternalCollaboratorMutationVariables>(UpdateExternalCollaboratorDocument, options);
      }
export type UpdateExternalCollaboratorMutationHookResult = ReturnType<typeof useUpdateExternalCollaboratorMutation>;
export type UpdateExternalCollaboratorMutationResult = Apollo.MutationResult<UpdateExternalCollaboratorMutation>;
export type UpdateExternalCollaboratorMutationOptions = Apollo.BaseMutationOptions<UpdateExternalCollaboratorMutation, UpdateExternalCollaboratorMutationVariables>;
export const DeleteExternalCollaboratorDocument = gql`
    mutation DeleteExternalCollaborator($input: DeleteExternalCollaboratorInput!) {
  deleteExternalCollaborator(input: $input) {
    success
    errors
  }
}
    `;
export type DeleteExternalCollaboratorMutationFn = Apollo.MutationFunction<DeleteExternalCollaboratorMutation, DeleteExternalCollaboratorMutationVariables>;

/**
 * __useDeleteExternalCollaboratorMutation__
 *
 * To run a mutation, you first call `useDeleteExternalCollaboratorMutation` within a React component and pass it any options that fit your needs.
 * When your component renders, `useDeleteExternalCollaboratorMutation` returns a tuple that includes:
 * - A mutate function that you can call at any time to execute the mutation
 * - An object with fields that represent the current status of the mutation's execution
 *
 * @param baseOptions options that will be passed into the mutation, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options-2;
 *
 * @example
 * const [deleteExternalCollaboratorMutation, { data, loading, error }] = useDeleteExternalCollaboratorMutation({
 *   variables: {
 *      input: // value for 'input'
 *   },
 * });
 */
export function useDeleteExternalCollaboratorMutation(baseOptions?: Apollo.MutationHookOptions<DeleteExternalCollaboratorMutation, DeleteExternalCollaboratorMutationVariables>) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useMutation<DeleteExternalCollaboratorMutation, DeleteExternalCollaboratorMutationVariables>(DeleteExternalCollaboratorDocument, options);
      }
export type DeleteExternalCollaboratorMutationHookResult = ReturnType<typeof useDeleteExternalCollaboratorMutation>;
export type DeleteExternalCollaboratorMutationResult = Apollo.MutationResult<DeleteExternalCollaboratorMutation>;
export type DeleteExternalCollaboratorMutationOptions = Apollo.BaseMutationOptions<DeleteExternalCollaboratorMutation, DeleteExternalCollaboratorMutationVariables>;
export const InviteOrganizationMemberDocument = gql`
    mutation InviteOrganizationMember($input: InviteOrganizationMemberInput!) {
  inviteOrganizationMember(input: $input) {
    success
    errors
  }
}
    `;
export type InviteOrganizationMemberMutationFn = Apollo.MutationFunction<InviteOrganizationMemberMutation, InviteOrganizationMemberMutationVariables>;

/**
 * __useInviteOrganizationMemberMutation__
 *
 * To run a mutation, you first call `useInviteOrganizationMemberMutation` within a React component and pass it any options that fit your needs.
 * When your component renders, `useInviteOrganizationMemberMutation` returns a tuple that includes:
 * - A mutate function that you can call at any time to execute the mutation
 * - An object with fields that represent the current status of the mutation's execution
 *
 * @param baseOptions options that will be passed into the mutation, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options-2;
 *
 * @example
 * const [inviteOrganizationMemberMutation, { data, loading, error }] = useInviteOrganizationMemberMutation({
 *   variables: {
 *      input: // value for 'input'
 *   },
 * });
 */
export function useInviteOrganizationMemberMutation(baseOptions?: Apollo.MutationHookOptions<InviteOrganizationMemberMutation, InviteOrganizationMemberMutationVariables>) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useMutation<InviteOrganizationMemberMutation, InviteOrganizationMemberMutationVariables>(InviteOrganizationMemberDocument, options);
      }
export type InviteOrganizationMemberMutationHookResult = ReturnType<typeof useInviteOrganizationMemberMutation>;
export type InviteOrganizationMemberMutationResult = Apollo.MutationResult<InviteOrganizationMemberMutation>;
export type InviteOrganizationMemberMutationOptions = Apollo.BaseMutationOptions<InviteOrganizationMemberMutation, InviteOrganizationMemberMutationVariables>;
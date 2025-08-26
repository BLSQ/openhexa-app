import * as Types from '../../../graphql/types';

import { gql } from '@apollo/client';
import { WorkspaceRoleFragmentDoc } from '../../components/WorkspaceRolesList.generated';
import { User_UserFragmentDoc } from '../../../core/features/User/User.generated';
import * as Apollo from '@apollo/client';
const defaultOptions = {} as const;
export type OrganizationMembersQueryVariables = Types.Exact<{
  id: Types.Scalars['UUID']['input'];
  page?: Types.InputMaybe<Types.Scalars['Int']['input']>;
  perPage?: Types.InputMaybe<Types.Scalars['Int']['input']>;
  term?: Types.InputMaybe<Types.Scalars['String']['input']>;
}>;


export type OrganizationMembersQuery = { __typename?: 'Query', organization?: { __typename?: 'Organization', id: string, permissions: { __typename?: 'OrganizationPermissions', manageMembers: boolean, manageOwners: boolean }, workspaces: { __typename?: 'WorkspacePage', items: Array<{ __typename?: 'Workspace', slug: string, name: string }> }, members: { __typename?: 'OrganizationMembershipPage', totalItems: number, items: Array<{ __typename?: 'OrganizationMembership', id: string, role: Types.OrganizationMembershipRole, createdAt: any, workspaceMemberships: Array<{ __typename?: 'WorkspaceMembership', id: string, role: Types.WorkspaceMembershipRole, workspace: { __typename?: 'Workspace', slug: string, name: string } }>, user: { __typename?: 'User', id: string, email: string, displayName: string, avatar: { __typename?: 'Avatar', initials: string, color: string } } }> } } | null };

export type UpdateOrganizationMemberMutationVariables = Types.Exact<{
  input: Types.UpdateOrganizationMemberInput;
}>;


export type UpdateOrganizationMemberMutation = { __typename?: 'Mutation', updateOrganizationMember: { __typename?: 'UpdateOrganizationMemberResult', success: boolean, errors: Array<Types.UpdateOrganizationMemberError>, membership?: { __typename?: 'OrganizationMembership', id: string, role: Types.OrganizationMembershipRole } | null } };

export type DeleteOrganizationMemberMutationVariables = Types.Exact<{
  input: Types.DeleteOrganizationMemberInput;
}>;


export type DeleteOrganizationMemberMutation = { __typename?: 'Mutation', deleteOrganizationMember: { __typename?: 'DeleteOrganizationMemberResult', success: boolean, errors: Array<Types.DeleteOrganizationMemberError> } };

export type InviteOrganizationMemberMutationVariables = Types.Exact<{
  input: Types.InviteOrganizationMemberInput;
}>;


export type InviteOrganizationMemberMutation = { __typename?: 'Mutation', inviteOrganizationMember: { __typename?: 'InviteOrganizationMemberResult', success: boolean, errors: Array<Types.InviteOrganizationMemberError> } };


export const OrganizationMembersDocument = gql`
    query OrganizationMembers($id: UUID!, $page: Int, $perPage: Int, $term: String) {
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
    members(page: $page, perPage: $perPage, term: $term) {
      totalItems
      items {
        id
        role
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
export const UpdateOrganizationMemberDocument = gql`
    mutation UpdateOrganizationMember($input: UpdateOrganizationMemberInput!) {
  updateOrganizationMember(input: $input) {
    success
    errors
    membership {
      id
      role
    }
  }
}
    `;
export type UpdateOrganizationMemberMutationFn = Apollo.MutationFunction<UpdateOrganizationMemberMutation, UpdateOrganizationMemberMutationVariables>;

/**
 * __useUpdateOrganizationMemberMutation__
 *
 * To run a mutation, you first call `useUpdateOrganizationMemberMutation` within a React component and pass it any options that fit your needs.
 * When your component renders, `useUpdateOrganizationMemberMutation` returns a tuple that includes:
 * - A mutate function that you can call at any time to execute the mutation
 * - An object with fields that represent the current status of the mutation's execution
 *
 * @param baseOptions options that will be passed into the mutation, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options-2;
 *
 * @example
 * const [updateOrganizationMemberMutation, { data, loading, error }] = useUpdateOrganizationMemberMutation({
 *   variables: {
 *      input: // value for 'input'
 *   },
 * });
 */
export function useUpdateOrganizationMemberMutation(baseOptions?: Apollo.MutationHookOptions<UpdateOrganizationMemberMutation, UpdateOrganizationMemberMutationVariables>) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useMutation<UpdateOrganizationMemberMutation, UpdateOrganizationMemberMutationVariables>(UpdateOrganizationMemberDocument, options);
      }
export type UpdateOrganizationMemberMutationHookResult = ReturnType<typeof useUpdateOrganizationMemberMutation>;
export type UpdateOrganizationMemberMutationResult = Apollo.MutationResult<UpdateOrganizationMemberMutation>;
export type UpdateOrganizationMemberMutationOptions = Apollo.BaseMutationOptions<UpdateOrganizationMemberMutation, UpdateOrganizationMemberMutationVariables>;
export const DeleteOrganizationMemberDocument = gql`
    mutation DeleteOrganizationMember($input: DeleteOrganizationMemberInput!) {
  deleteOrganizationMember(input: $input) {
    success
    errors
  }
}
    `;
export type DeleteOrganizationMemberMutationFn = Apollo.MutationFunction<DeleteOrganizationMemberMutation, DeleteOrganizationMemberMutationVariables>;

/**
 * __useDeleteOrganizationMemberMutation__
 *
 * To run a mutation, you first call `useDeleteOrganizationMemberMutation` within a React component and pass it any options that fit your needs.
 * When your component renders, `useDeleteOrganizationMemberMutation` returns a tuple that includes:
 * - A mutate function that you can call at any time to execute the mutation
 * - An object with fields that represent the current status of the mutation's execution
 *
 * @param baseOptions options that will be passed into the mutation, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options-2;
 *
 * @example
 * const [deleteOrganizationMemberMutation, { data, loading, error }] = useDeleteOrganizationMemberMutation({
 *   variables: {
 *      input: // value for 'input'
 *   },
 * });
 */
export function useDeleteOrganizationMemberMutation(baseOptions?: Apollo.MutationHookOptions<DeleteOrganizationMemberMutation, DeleteOrganizationMemberMutationVariables>) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useMutation<DeleteOrganizationMemberMutation, DeleteOrganizationMemberMutationVariables>(DeleteOrganizationMemberDocument, options);
      }
export type DeleteOrganizationMemberMutationHookResult = ReturnType<typeof useDeleteOrganizationMemberMutation>;
export type DeleteOrganizationMemberMutationResult = Apollo.MutationResult<DeleteOrganizationMemberMutation>;
export type DeleteOrganizationMemberMutationOptions = Apollo.BaseMutationOptions<DeleteOrganizationMemberMutation, DeleteOrganizationMemberMutationVariables>;
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
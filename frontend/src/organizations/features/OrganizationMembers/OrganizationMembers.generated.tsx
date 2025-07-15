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

export type UpdateOrganizationMemberMutationVariables = Types.Exact<{
  input: Types.UpdateOrganizationMemberInput;
}>;


export type UpdateOrganizationMemberMutation = { __typename?: 'Mutation', updateOrganizationMember: { __typename?: 'UpdateOrganizationMemberResult', success: boolean, errors: Array<Types.UpdateOrganizationMemberError>, membership?: { __typename?: 'OrganizationMembership', id: string, role: Types.OrganizationMembershipRole } | null } };

export type AddOrganizationMemberMutationVariables = Types.Exact<{
  input: Types.AddOrganizationMemberInput;
}>;


export type AddOrganizationMemberMutation = { __typename?: 'Mutation', addOrganizationMember: { __typename?: 'AddOrganizationMemberResult', success: boolean, errors: Array<Types.AddOrganizationMemberError>, membership?: { __typename?: 'OrganizationMembership', id: string, role: Types.OrganizationMembershipRole, user: { __typename?: 'User', id: string, displayName: string, email: string } } | null } };

export type DeleteOrganizationMemberMutationVariables = Types.Exact<{
  input: Types.DeleteOrganizationMemberInput;
}>;


export type DeleteOrganizationMemberMutation = { __typename?: 'Mutation', deleteOrganizationMember: { __typename?: 'DeleteOrganizationMemberResult', success: boolean, errors: Array<Types.DeleteOrganizationMemberError> } };


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
export const AddOrganizationMemberDocument = gql`
    mutation AddOrganizationMember($input: AddOrganizationMemberInput!) {
  addOrganizationMember(input: $input) {
    success
    errors
    membership {
      id
      user {
        id
        displayName
        email
      }
      role
    }
  }
}
    `;
export type AddOrganizationMemberMutationFn = Apollo.MutationFunction<AddOrganizationMemberMutation, AddOrganizationMemberMutationVariables>;

/**
 * __useAddOrganizationMemberMutation__
 *
 * To run a mutation, you first call `useAddOrganizationMemberMutation` within a React component and pass it any options that fit your needs.
 * When your component renders, `useAddOrganizationMemberMutation` returns a tuple that includes:
 * - A mutate function that you can call at any time to execute the mutation
 * - An object with fields that represent the current status of the mutation's execution
 *
 * @param baseOptions options that will be passed into the mutation, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options-2;
 *
 * @example
 * const [addOrganizationMemberMutation, { data, loading, error }] = useAddOrganizationMemberMutation({
 *   variables: {
 *      input: // value for 'input'
 *   },
 * });
 */
export function useAddOrganizationMemberMutation(baseOptions?: Apollo.MutationHookOptions<AddOrganizationMemberMutation, AddOrganizationMemberMutationVariables>) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useMutation<AddOrganizationMemberMutation, AddOrganizationMemberMutationVariables>(AddOrganizationMemberDocument, options);
      }
export type AddOrganizationMemberMutationHookResult = ReturnType<typeof useAddOrganizationMemberMutation>;
export type AddOrganizationMemberMutationResult = Apollo.MutationResult<AddOrganizationMemberMutation>;
export type AddOrganizationMemberMutationOptions = Apollo.BaseMutationOptions<AddOrganizationMemberMutation, AddOrganizationMemberMutationVariables>;
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
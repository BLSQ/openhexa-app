import * as Types from '../../graphql-types';

import { gql } from '@apollo/client';
import * as Apollo from '@apollo/client';
const defaultOptions = {} as const;
export type CreateWorkspaceMutationVariables = Types.Exact<{
  input: Types.CreateWorkspaceInput;
}>;


export type CreateWorkspaceMutation = { __typename?: 'Mutation', createWorkspace: { __typename?: 'CreateWorkspaceResult', success: boolean, errors: Array<Types.CreateWorkspaceError>, workspace?: { __typename?: 'Workspace', slug: string, name: string, description?: string | null, countries: Array<{ __typename?: 'Country', code: string, alpha3: string, name: string }> } | null } };

export type UpdateWorkspaceMutationVariables = Types.Exact<{
  input: Types.UpdateWorkspaceInput;
}>;


export type UpdateWorkspaceMutation = { __typename?: 'Mutation', updateWorkspace: { __typename?: 'UpdateWorkspaceResult', success: boolean, errors: Array<Types.UpdateWorkspaceError>, workspace?: { __typename?: 'Workspace', slug: string, name: string, description?: string | null, countries: Array<{ __typename?: 'Country', code: string, alpha3: string, name: string }> } | null } };

export type DeleteWorkspaceMutationVariables = Types.Exact<{
  input: Types.DeleteWorkspaceInput;
}>;


export type DeleteWorkspaceMutation = { __typename?: 'Mutation', deleteWorkspace: { __typename?: 'DeleteWorkspaceResult', success: boolean, errors: Array<Types.DeleteWorkspaceError> } };

export type InviteWorkspaceMemberMutationVariables = Types.Exact<{
  input: Types.InviteWorkspaceMemberInput;
}>;


export type InviteWorkspaceMemberMutation = { __typename?: 'Mutation', inviteWorkspaceMember: { __typename?: 'InviteWorkspaceMemberResult', success: boolean, errors: Array<Types.InviteWorkspaceMembershipError>, workspaceMembership?: { __typename?: 'WorkspaceMembership', id: string } | null } };

export type DeleteWorkspaceMemberMutationVariables = Types.Exact<{
  input: Types.DeleteWorkspaceMemberInput;
}>;


export type DeleteWorkspaceMemberMutation = { __typename?: 'Mutation', deleteWorkspaceMember: { __typename?: 'DeleteWorkspaceMemberResult', success: boolean, errors: Array<Types.DeleteWorkspaceMemberError> } };

export type UpdateWorkspaceMemberMutationVariables = Types.Exact<{
  input: Types.UpdateWorkspaceMemberInput;
}>;


export type UpdateWorkspaceMemberMutation = { __typename?: 'Mutation', updateWorkspaceMember: { __typename?: 'UpdateWorkspaceMemberResult', success: boolean, errors: Array<Types.UpdateWorkspaceMemberError>, workspaceMembership?: { __typename?: 'WorkspaceMembership', id: string, role: Types.WorkspaceMembershipRole } | null } };

export type CreateConnectionMutationVariables = Types.Exact<{
  input: Types.CreateConnectionInput;
}>;


export type CreateConnectionMutation = { __typename?: 'Mutation', createConnection: { __typename?: 'CreateConnectionResult', success: boolean, errors: Array<Types.CreateConnectionError>, connection?: { __typename?: 'Connection', id: string, name: string } | null } };

export type UpdateConnectionMutationVariables = Types.Exact<{
  input: Types.UpdateConnectionInput;
}>;


export type UpdateConnectionMutation = { __typename?: 'Mutation', updateConnection: { __typename?: 'UpdateConnectionResult', success: boolean, errors: Array<Types.UpdateConnectionError>, connection?: { __typename?: 'Connection', id: string, name: string, slug: string, description?: string | null } | null } };


export const CreateWorkspaceDocument = gql`
    mutation createWorkspace($input: CreateWorkspaceInput!) {
  createWorkspace(input: $input) {
    success
    workspace {
      slug
      name
      description
      countries {
        code
        alpha3
        name
      }
    }
    errors
  }
}
    `;
export type CreateWorkspaceMutationFn = Apollo.MutationFunction<CreateWorkspaceMutation, CreateWorkspaceMutationVariables>;

/**
 * __useCreateWorkspaceMutation__
 *
 * To run a mutation, you first call `useCreateWorkspaceMutation` within a React component and pass it any options that fit your needs.
 * When your component renders, `useCreateWorkspaceMutation` returns a tuple that includes:
 * - A mutate function that you can call at any time to execute the mutation
 * - An object with fields that represent the current status of the mutation's execution
 *
 * @param baseOptions options that will be passed into the mutation, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options-2;
 *
 * @example
 * const [createWorkspaceMutation, { data, loading, error }] = useCreateWorkspaceMutation({
 *   variables: {
 *      input: // value for 'input'
 *   },
 * });
 */
export function useCreateWorkspaceMutation(baseOptions?: Apollo.MutationHookOptions<CreateWorkspaceMutation, CreateWorkspaceMutationVariables>) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useMutation<CreateWorkspaceMutation, CreateWorkspaceMutationVariables>(CreateWorkspaceDocument, options);
      }
export type CreateWorkspaceMutationHookResult = ReturnType<typeof useCreateWorkspaceMutation>;
export type CreateWorkspaceMutationResult = Apollo.MutationResult<CreateWorkspaceMutation>;
export type CreateWorkspaceMutationOptions = Apollo.BaseMutationOptions<CreateWorkspaceMutation, CreateWorkspaceMutationVariables>;
export const UpdateWorkspaceDocument = gql`
    mutation updateWorkspace($input: UpdateWorkspaceInput!) {
  updateWorkspace(input: $input) {
    success
    workspace {
      slug
      name
      description
      countries {
        code
        alpha3
        name
      }
    }
    errors
  }
}
    `;
export type UpdateWorkspaceMutationFn = Apollo.MutationFunction<UpdateWorkspaceMutation, UpdateWorkspaceMutationVariables>;

/**
 * __useUpdateWorkspaceMutation__
 *
 * To run a mutation, you first call `useUpdateWorkspaceMutation` within a React component and pass it any options that fit your needs.
 * When your component renders, `useUpdateWorkspaceMutation` returns a tuple that includes:
 * - A mutate function that you can call at any time to execute the mutation
 * - An object with fields that represent the current status of the mutation's execution
 *
 * @param baseOptions options that will be passed into the mutation, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options-2;
 *
 * @example
 * const [updateWorkspaceMutation, { data, loading, error }] = useUpdateWorkspaceMutation({
 *   variables: {
 *      input: // value for 'input'
 *   },
 * });
 */
export function useUpdateWorkspaceMutation(baseOptions?: Apollo.MutationHookOptions<UpdateWorkspaceMutation, UpdateWorkspaceMutationVariables>) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useMutation<UpdateWorkspaceMutation, UpdateWorkspaceMutationVariables>(UpdateWorkspaceDocument, options);
      }
export type UpdateWorkspaceMutationHookResult = ReturnType<typeof useUpdateWorkspaceMutation>;
export type UpdateWorkspaceMutationResult = Apollo.MutationResult<UpdateWorkspaceMutation>;
export type UpdateWorkspaceMutationOptions = Apollo.BaseMutationOptions<UpdateWorkspaceMutation, UpdateWorkspaceMutationVariables>;
export const DeleteWorkspaceDocument = gql`
    mutation deleteWorkspace($input: DeleteWorkspaceInput!) {
  deleteWorkspace(input: $input) {
    success
    errors
  }
}
    `;
export type DeleteWorkspaceMutationFn = Apollo.MutationFunction<DeleteWorkspaceMutation, DeleteWorkspaceMutationVariables>;

/**
 * __useDeleteWorkspaceMutation__
 *
 * To run a mutation, you first call `useDeleteWorkspaceMutation` within a React component and pass it any options that fit your needs.
 * When your component renders, `useDeleteWorkspaceMutation` returns a tuple that includes:
 * - A mutate function that you can call at any time to execute the mutation
 * - An object with fields that represent the current status of the mutation's execution
 *
 * @param baseOptions options that will be passed into the mutation, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options-2;
 *
 * @example
 * const [deleteWorkspaceMutation, { data, loading, error }] = useDeleteWorkspaceMutation({
 *   variables: {
 *      input: // value for 'input'
 *   },
 * });
 */
export function useDeleteWorkspaceMutation(baseOptions?: Apollo.MutationHookOptions<DeleteWorkspaceMutation, DeleteWorkspaceMutationVariables>) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useMutation<DeleteWorkspaceMutation, DeleteWorkspaceMutationVariables>(DeleteWorkspaceDocument, options);
      }
export type DeleteWorkspaceMutationHookResult = ReturnType<typeof useDeleteWorkspaceMutation>;
export type DeleteWorkspaceMutationResult = Apollo.MutationResult<DeleteWorkspaceMutation>;
export type DeleteWorkspaceMutationOptions = Apollo.BaseMutationOptions<DeleteWorkspaceMutation, DeleteWorkspaceMutationVariables>;
export const InviteWorkspaceMemberDocument = gql`
    mutation inviteWorkspaceMember($input: InviteWorkspaceMemberInput!) {
  inviteWorkspaceMember(input: $input) {
    success
    errors
    workspaceMembership {
      id
    }
  }
}
    `;
export type InviteWorkspaceMemberMutationFn = Apollo.MutationFunction<InviteWorkspaceMemberMutation, InviteWorkspaceMemberMutationVariables>;

/**
 * __useInviteWorkspaceMemberMutation__
 *
 * To run a mutation, you first call `useInviteWorkspaceMemberMutation` within a React component and pass it any options that fit your needs.
 * When your component renders, `useInviteWorkspaceMemberMutation` returns a tuple that includes:
 * - A mutate function that you can call at any time to execute the mutation
 * - An object with fields that represent the current status of the mutation's execution
 *
 * @param baseOptions options that will be passed into the mutation, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options-2;
 *
 * @example
 * const [inviteWorkspaceMemberMutation, { data, loading, error }] = useInviteWorkspaceMemberMutation({
 *   variables: {
 *      input: // value for 'input'
 *   },
 * });
 */
export function useInviteWorkspaceMemberMutation(baseOptions?: Apollo.MutationHookOptions<InviteWorkspaceMemberMutation, InviteWorkspaceMemberMutationVariables>) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useMutation<InviteWorkspaceMemberMutation, InviteWorkspaceMemberMutationVariables>(InviteWorkspaceMemberDocument, options);
      }
export type InviteWorkspaceMemberMutationHookResult = ReturnType<typeof useInviteWorkspaceMemberMutation>;
export type InviteWorkspaceMemberMutationResult = Apollo.MutationResult<InviteWorkspaceMemberMutation>;
export type InviteWorkspaceMemberMutationOptions = Apollo.BaseMutationOptions<InviteWorkspaceMemberMutation, InviteWorkspaceMemberMutationVariables>;
export const DeleteWorkspaceMemberDocument = gql`
    mutation deleteWorkspaceMember($input: DeleteWorkspaceMemberInput!) {
  deleteWorkspaceMember(input: $input) {
    success
    errors
  }
}
    `;
export type DeleteWorkspaceMemberMutationFn = Apollo.MutationFunction<DeleteWorkspaceMemberMutation, DeleteWorkspaceMemberMutationVariables>;

/**
 * __useDeleteWorkspaceMemberMutation__
 *
 * To run a mutation, you first call `useDeleteWorkspaceMemberMutation` within a React component and pass it any options that fit your needs.
 * When your component renders, `useDeleteWorkspaceMemberMutation` returns a tuple that includes:
 * - A mutate function that you can call at any time to execute the mutation
 * - An object with fields that represent the current status of the mutation's execution
 *
 * @param baseOptions options that will be passed into the mutation, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options-2;
 *
 * @example
 * const [deleteWorkspaceMemberMutation, { data, loading, error }] = useDeleteWorkspaceMemberMutation({
 *   variables: {
 *      input: // value for 'input'
 *   },
 * });
 */
export function useDeleteWorkspaceMemberMutation(baseOptions?: Apollo.MutationHookOptions<DeleteWorkspaceMemberMutation, DeleteWorkspaceMemberMutationVariables>) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useMutation<DeleteWorkspaceMemberMutation, DeleteWorkspaceMemberMutationVariables>(DeleteWorkspaceMemberDocument, options);
      }
export type DeleteWorkspaceMemberMutationHookResult = ReturnType<typeof useDeleteWorkspaceMemberMutation>;
export type DeleteWorkspaceMemberMutationResult = Apollo.MutationResult<DeleteWorkspaceMemberMutation>;
export type DeleteWorkspaceMemberMutationOptions = Apollo.BaseMutationOptions<DeleteWorkspaceMemberMutation, DeleteWorkspaceMemberMutationVariables>;
export const UpdateWorkspaceMemberDocument = gql`
    mutation updateWorkspaceMember($input: UpdateWorkspaceMemberInput!) {
  updateWorkspaceMember(input: $input) {
    success
    errors
    workspaceMembership {
      id
      role
    }
  }
}
    `;
export type UpdateWorkspaceMemberMutationFn = Apollo.MutationFunction<UpdateWorkspaceMemberMutation, UpdateWorkspaceMemberMutationVariables>;

/**
 * __useUpdateWorkspaceMemberMutation__
 *
 * To run a mutation, you first call `useUpdateWorkspaceMemberMutation` within a React component and pass it any options that fit your needs.
 * When your component renders, `useUpdateWorkspaceMemberMutation` returns a tuple that includes:
 * - A mutate function that you can call at any time to execute the mutation
 * - An object with fields that represent the current status of the mutation's execution
 *
 * @param baseOptions options that will be passed into the mutation, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options-2;
 *
 * @example
 * const [updateWorkspaceMemberMutation, { data, loading, error }] = useUpdateWorkspaceMemberMutation({
 *   variables: {
 *      input: // value for 'input'
 *   },
 * });
 */
export function useUpdateWorkspaceMemberMutation(baseOptions?: Apollo.MutationHookOptions<UpdateWorkspaceMemberMutation, UpdateWorkspaceMemberMutationVariables>) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useMutation<UpdateWorkspaceMemberMutation, UpdateWorkspaceMemberMutationVariables>(UpdateWorkspaceMemberDocument, options);
      }
export type UpdateWorkspaceMemberMutationHookResult = ReturnType<typeof useUpdateWorkspaceMemberMutation>;
export type UpdateWorkspaceMemberMutationResult = Apollo.MutationResult<UpdateWorkspaceMemberMutation>;
export type UpdateWorkspaceMemberMutationOptions = Apollo.BaseMutationOptions<UpdateWorkspaceMemberMutation, UpdateWorkspaceMemberMutationVariables>;
export const CreateConnectionDocument = gql`
    mutation createConnection($input: CreateConnectionInput!) {
  createConnection(input: $input) {
    success
    connection {
      id
      name
    }
    errors
  }
}
    `;
export type CreateConnectionMutationFn = Apollo.MutationFunction<CreateConnectionMutation, CreateConnectionMutationVariables>;

/**
 * __useCreateConnectionMutation__
 *
 * To run a mutation, you first call `useCreateConnectionMutation` within a React component and pass it any options that fit your needs.
 * When your component renders, `useCreateConnectionMutation` returns a tuple that includes:
 * - A mutate function that you can call at any time to execute the mutation
 * - An object with fields that represent the current status of the mutation's execution
 *
 * @param baseOptions options that will be passed into the mutation, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options-2;
 *
 * @example
 * const [createConnectionMutation, { data, loading, error }] = useCreateConnectionMutation({
 *   variables: {
 *      input: // value for 'input'
 *   },
 * });
 */
export function useCreateConnectionMutation(baseOptions?: Apollo.MutationHookOptions<CreateConnectionMutation, CreateConnectionMutationVariables>) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useMutation<CreateConnectionMutation, CreateConnectionMutationVariables>(CreateConnectionDocument, options);
      }
export type CreateConnectionMutationHookResult = ReturnType<typeof useCreateConnectionMutation>;
export type CreateConnectionMutationResult = Apollo.MutationResult<CreateConnectionMutation>;
export type CreateConnectionMutationOptions = Apollo.BaseMutationOptions<CreateConnectionMutation, CreateConnectionMutationVariables>;
export const UpdateConnectionDocument = gql`
    mutation updateConnection($input: UpdateConnectionInput!) {
  updateConnection(input: $input) {
    success
    errors
    connection {
      id
      name
      slug
      description
    }
  }
}
    `;
export type UpdateConnectionMutationFn = Apollo.MutationFunction<UpdateConnectionMutation, UpdateConnectionMutationVariables>;

/**
 * __useUpdateConnectionMutation__
 *
 * To run a mutation, you first call `useUpdateConnectionMutation` within a React component and pass it any options that fit your needs.
 * When your component renders, `useUpdateConnectionMutation` returns a tuple that includes:
 * - A mutate function that you can call at any time to execute the mutation
 * - An object with fields that represent the current status of the mutation's execution
 *
 * @param baseOptions options that will be passed into the mutation, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options-2;
 *
 * @example
 * const [updateConnectionMutation, { data, loading, error }] = useUpdateConnectionMutation({
 *   variables: {
 *      input: // value for 'input'
 *   },
 * });
 */
export function useUpdateConnectionMutation(baseOptions?: Apollo.MutationHookOptions<UpdateConnectionMutation, UpdateConnectionMutationVariables>) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useMutation<UpdateConnectionMutation, UpdateConnectionMutationVariables>(UpdateConnectionDocument, options);
      }
export type UpdateConnectionMutationHookResult = ReturnType<typeof useUpdateConnectionMutation>;
export type UpdateConnectionMutationResult = Apollo.MutationResult<UpdateConnectionMutation>;
export type UpdateConnectionMutationOptions = Apollo.BaseMutationOptions<UpdateConnectionMutation, UpdateConnectionMutationVariables>;
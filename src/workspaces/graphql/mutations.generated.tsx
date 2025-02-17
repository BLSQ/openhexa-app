import * as Types from '../../graphql/types';

import { gql } from '@apollo/client';
import { User_UserFragmentDoc } from '../../core/features/User/User.generated';
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

export type ArchiveWorkspaceMutationVariables = Types.Exact<{
  input: Types.ArchiveWorkspaceInput;
}>;


export type ArchiveWorkspaceMutation = { __typename?: 'Mutation', archiveWorkspace: { __typename?: 'ArchiveWorkspaceResult', success: boolean, errors: Array<Types.ArchiveWorkspaceError> } };

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


export type CreateConnectionMutation = { __typename?: 'Mutation', createConnection: { __typename?: 'CreateConnectionResult', success: boolean, errors: Array<Types.CreateConnectionError>, connection?: { __typename?: 'CustomConnection', id: string, name: string } | { __typename?: 'DHIS2Connection', id: string, name: string } | { __typename?: 'GCSConnection', id: string, name: string } | { __typename?: 'IASOConnection', id: string, name: string } | { __typename?: 'PostgreSQLConnection', id: string, name: string } | { __typename?: 'S3Connection', id: string, name: string } | null } };

export type UpdateConnectionMutationVariables = Types.Exact<{
  input: Types.UpdateConnectionInput;
}>;


export type UpdateConnectionMutation = { __typename?: 'Mutation', updateConnection: { __typename?: 'UpdateConnectionResult', success: boolean, errors: Array<Types.UpdateConnectionError>, connection?: { __typename?: 'CustomConnection', id: string, name: string, slug: string, description?: string | null, fields: Array<{ __typename?: 'ConnectionField', code: string, value?: string | null, secret: boolean }> } | { __typename?: 'DHIS2Connection', id: string, name: string, slug: string, description?: string | null, fields: Array<{ __typename?: 'ConnectionField', code: string, value?: string | null, secret: boolean }> } | { __typename?: 'GCSConnection', id: string, name: string, slug: string, description?: string | null, fields: Array<{ __typename?: 'ConnectionField', code: string, value?: string | null, secret: boolean }> } | { __typename?: 'IASOConnection', id: string, name: string, slug: string, description?: string | null, fields: Array<{ __typename?: 'ConnectionField', code: string, value?: string | null, secret: boolean }> } | { __typename?: 'PostgreSQLConnection', id: string, name: string, slug: string, description?: string | null, fields: Array<{ __typename?: 'ConnectionField', code: string, value?: string | null, secret: boolean }> } | { __typename?: 'S3Connection', id: string, name: string, slug: string, description?: string | null, fields: Array<{ __typename?: 'ConnectionField', code: string, value?: string | null, secret: boolean }> } | null } };

export type GenerateNewDatabasePasswordMutationVariables = Types.Exact<{
  input: Types.GenerateNewDatabasePasswordInput;
}>;


export type GenerateNewDatabasePasswordMutation = { __typename?: 'Mutation', generateNewDatabasePassword: { __typename?: 'GenerateNewDatabasePasswordResult', success: boolean, errors: Array<Types.GenerateNewDatabasePasswordError> } };

export type CreatePipelineMutationVariables = Types.Exact<{
  input: Types.CreatePipelineInput;
}>;


export type CreatePipelineMutation = { __typename?: 'Mutation', createPipeline: { __typename?: 'CreatePipelineResult', success: boolean, errors: Array<Types.PipelineError>, pipeline?: { __typename?: 'Pipeline', code: string } | null } };

export type DeletePipelineMutationVariables = Types.Exact<{
  input: Types.DeletePipelineInput;
}>;


export type DeletePipelineMutation = { __typename?: 'Mutation', deletePipeline: { __typename?: 'DeletePipelineResult', success: boolean, errors: Array<Types.PipelineError> } };

export type StopPipelineMutationVariables = Types.Exact<{
  input: Types.StopPipelineInput;
}>;


export type StopPipelineMutation = { __typename?: 'Mutation', stopPipeline: { __typename?: 'StopPipelineResult', success: boolean, errors: Array<Types.PipelineError> } };

export type DeletePipelineVersionMutationVariables = Types.Exact<{
  input: Types.DeletePipelineVersionInput;
}>;


export type DeletePipelineVersionMutation = { __typename?: 'Mutation', deletePipelineVersion: { __typename?: 'DeletePipelineVersionResult', success: boolean, errors: Array<Types.DeletePipelineVersionError> } };

export type DeletePipelineTemplateMutationVariables = Types.Exact<{
  input: Types.DeletePipelineTemplateInput;
}>;


export type DeletePipelineTemplateMutation = { __typename?: 'Mutation', deletePipelineTemplate: { __typename?: 'DeletePipelineTemplateResult', success: boolean, errors: Array<Types.PipelineTemplateError> } };

export type JoinWorkspaceMutationVariables = Types.Exact<{
  input: Types.JoinWorkspaceInput;
}>;


export type JoinWorkspaceMutation = { __typename?: 'Mutation', joinWorkspace: { __typename?: 'JoinWorkspaceResult', success: boolean, errors: Array<Types.JoinWorkspaceError>, invitation?: { __typename?: 'WorkspaceInvitation', id: string, status: Types.WorkspaceInvitationStatus, role: Types.WorkspaceMembershipRole, createdAt: any, invitedBy?: { __typename?: 'User', id: string, email: string, displayName: string, avatar: { __typename?: 'Avatar', initials: string, color: string } } | null, workspace: { __typename?: 'Workspace', slug: string, name: string } } | null, workspace?: { __typename?: 'Workspace', slug: string } | null } };

export type DeclineWorkspaceInvitationMutationVariables = Types.Exact<{
  input: Types.DeclineWorkspaceInvitationInput;
}>;


export type DeclineWorkspaceInvitationMutation = { __typename?: 'Mutation', declineWorkspaceInvitation: { __typename?: 'DeclineWorkspaceInvitationResult', success: boolean, errors: Array<Types.DeclineWorkspaceInvitationError>, invitation?: { __typename?: 'WorkspaceInvitation', id: string, status: Types.WorkspaceInvitationStatus } | null } };

export type DeleteWorkspaceInvitationMutationVariables = Types.Exact<{
  input: Types.DeleteWorkspaceInvitationInput;
}>;


export type DeleteWorkspaceInvitationMutation = { __typename?: 'Mutation', deleteWorkspaceInvitation: { __typename?: 'DeleteWorkspaceInvitationResult', success: boolean, errors: Array<Types.DeleteWorkspaceInvitationError> } };

export type ResendWorkspaceInvitationMutationVariables = Types.Exact<{
  input: Types.ResendWorkspaceInvitationInput;
}>;


export type ResendWorkspaceInvitationMutation = { __typename?: 'Mutation', resendWorkspaceInvitation: { __typename?: 'ResendWorkspaceInvitationResult', success: boolean, errors: Array<Types.ResendWorkspaceInvitationError> } };

export type AddPipelineRecipientMutationVariables = Types.Exact<{
  input: Types.CreatePipelineRecipientInput;
}>;


export type AddPipelineRecipientMutation = { __typename?: 'Mutation', addPipelineRecipient: { __typename?: 'AddPipelineRecipientResult', success: boolean, errors: Array<Types.PipelineRecipientError> } };


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
export const ArchiveWorkspaceDocument = gql`
    mutation archiveWorkspace($input: ArchiveWorkspaceInput!) {
  archiveWorkspace(input: $input) {
    success
    errors
  }
}
    `;
export type ArchiveWorkspaceMutationFn = Apollo.MutationFunction<ArchiveWorkspaceMutation, ArchiveWorkspaceMutationVariables>;

/**
 * __useArchiveWorkspaceMutation__
 *
 * To run a mutation, you first call `useArchiveWorkspaceMutation` within a React component and pass it any options that fit your needs.
 * When your component renders, `useArchiveWorkspaceMutation` returns a tuple that includes:
 * - A mutate function that you can call at any time to execute the mutation
 * - An object with fields that represent the current status of the mutation's execution
 *
 * @param baseOptions options that will be passed into the mutation, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options-2;
 *
 * @example
 * const [archiveWorkspaceMutation, { data, loading, error }] = useArchiveWorkspaceMutation({
 *   variables: {
 *      input: // value for 'input'
 *   },
 * });
 */
export function useArchiveWorkspaceMutation(baseOptions?: Apollo.MutationHookOptions<ArchiveWorkspaceMutation, ArchiveWorkspaceMutationVariables>) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useMutation<ArchiveWorkspaceMutation, ArchiveWorkspaceMutationVariables>(ArchiveWorkspaceDocument, options);
      }
export type ArchiveWorkspaceMutationHookResult = ReturnType<typeof useArchiveWorkspaceMutation>;
export type ArchiveWorkspaceMutationResult = Apollo.MutationResult<ArchiveWorkspaceMutation>;
export type ArchiveWorkspaceMutationOptions = Apollo.BaseMutationOptions<ArchiveWorkspaceMutation, ArchiveWorkspaceMutationVariables>;
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
      fields {
        code
        value
        secret
      }
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
export const GenerateNewDatabasePasswordDocument = gql`
    mutation generateNewDatabasePassword($input: GenerateNewDatabasePasswordInput!) {
  generateNewDatabasePassword(input: $input) {
    success
    errors
  }
}
    `;
export type GenerateNewDatabasePasswordMutationFn = Apollo.MutationFunction<GenerateNewDatabasePasswordMutation, GenerateNewDatabasePasswordMutationVariables>;

/**
 * __useGenerateNewDatabasePasswordMutation__
 *
 * To run a mutation, you first call `useGenerateNewDatabasePasswordMutation` within a React component and pass it any options that fit your needs.
 * When your component renders, `useGenerateNewDatabasePasswordMutation` returns a tuple that includes:
 * - A mutate function that you can call at any time to execute the mutation
 * - An object with fields that represent the current status of the mutation's execution
 *
 * @param baseOptions options that will be passed into the mutation, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options-2;
 *
 * @example
 * const [generateNewDatabasePasswordMutation, { data, loading, error }] = useGenerateNewDatabasePasswordMutation({
 *   variables: {
 *      input: // value for 'input'
 *   },
 * });
 */
export function useGenerateNewDatabasePasswordMutation(baseOptions?: Apollo.MutationHookOptions<GenerateNewDatabasePasswordMutation, GenerateNewDatabasePasswordMutationVariables>) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useMutation<GenerateNewDatabasePasswordMutation, GenerateNewDatabasePasswordMutationVariables>(GenerateNewDatabasePasswordDocument, options);
      }
export type GenerateNewDatabasePasswordMutationHookResult = ReturnType<typeof useGenerateNewDatabasePasswordMutation>;
export type GenerateNewDatabasePasswordMutationResult = Apollo.MutationResult<GenerateNewDatabasePasswordMutation>;
export type GenerateNewDatabasePasswordMutationOptions = Apollo.BaseMutationOptions<GenerateNewDatabasePasswordMutation, GenerateNewDatabasePasswordMutationVariables>;
export const CreatePipelineDocument = gql`
    mutation createPipeline($input: CreatePipelineInput!) {
  createPipeline(input: $input) {
    success
    errors
    pipeline {
      code
    }
  }
}
    `;
export type CreatePipelineMutationFn = Apollo.MutationFunction<CreatePipelineMutation, CreatePipelineMutationVariables>;

/**
 * __useCreatePipelineMutation__
 *
 * To run a mutation, you first call `useCreatePipelineMutation` within a React component and pass it any options that fit your needs.
 * When your component renders, `useCreatePipelineMutation` returns a tuple that includes:
 * - A mutate function that you can call at any time to execute the mutation
 * - An object with fields that represent the current status of the mutation's execution
 *
 * @param baseOptions options that will be passed into the mutation, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options-2;
 *
 * @example
 * const [createPipelineMutation, { data, loading, error }] = useCreatePipelineMutation({
 *   variables: {
 *      input: // value for 'input'
 *   },
 * });
 */
export function useCreatePipelineMutation(baseOptions?: Apollo.MutationHookOptions<CreatePipelineMutation, CreatePipelineMutationVariables>) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useMutation<CreatePipelineMutation, CreatePipelineMutationVariables>(CreatePipelineDocument, options);
      }
export type CreatePipelineMutationHookResult = ReturnType<typeof useCreatePipelineMutation>;
export type CreatePipelineMutationResult = Apollo.MutationResult<CreatePipelineMutation>;
export type CreatePipelineMutationOptions = Apollo.BaseMutationOptions<CreatePipelineMutation, CreatePipelineMutationVariables>;
export const DeletePipelineDocument = gql`
    mutation deletePipeline($input: DeletePipelineInput!) {
  deletePipeline(input: $input) {
    success
    errors
  }
}
    `;
export type DeletePipelineMutationFn = Apollo.MutationFunction<DeletePipelineMutation, DeletePipelineMutationVariables>;

/**
 * __useDeletePipelineMutation__
 *
 * To run a mutation, you first call `useDeletePipelineMutation` within a React component and pass it any options that fit your needs.
 * When your component renders, `useDeletePipelineMutation` returns a tuple that includes:
 * - A mutate function that you can call at any time to execute the mutation
 * - An object with fields that represent the current status of the mutation's execution
 *
 * @param baseOptions options that will be passed into the mutation, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options-2;
 *
 * @example
 * const [deletePipelineMutation, { data, loading, error }] = useDeletePipelineMutation({
 *   variables: {
 *      input: // value for 'input'
 *   },
 * });
 */
export function useDeletePipelineMutation(baseOptions?: Apollo.MutationHookOptions<DeletePipelineMutation, DeletePipelineMutationVariables>) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useMutation<DeletePipelineMutation, DeletePipelineMutationVariables>(DeletePipelineDocument, options);
      }
export type DeletePipelineMutationHookResult = ReturnType<typeof useDeletePipelineMutation>;
export type DeletePipelineMutationResult = Apollo.MutationResult<DeletePipelineMutation>;
export type DeletePipelineMutationOptions = Apollo.BaseMutationOptions<DeletePipelineMutation, DeletePipelineMutationVariables>;
export const StopPipelineDocument = gql`
    mutation stopPipeline($input: StopPipelineInput!) {
  stopPipeline(input: $input) {
    success
    errors
  }
}
    `;
export type StopPipelineMutationFn = Apollo.MutationFunction<StopPipelineMutation, StopPipelineMutationVariables>;

/**
 * __useStopPipelineMutation__
 *
 * To run a mutation, you first call `useStopPipelineMutation` within a React component and pass it any options that fit your needs.
 * When your component renders, `useStopPipelineMutation` returns a tuple that includes:
 * - A mutate function that you can call at any time to execute the mutation
 * - An object with fields that represent the current status of the mutation's execution
 *
 * @param baseOptions options that will be passed into the mutation, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options-2;
 *
 * @example
 * const [stopPipelineMutation, { data, loading, error }] = useStopPipelineMutation({
 *   variables: {
 *      input: // value for 'input'
 *   },
 * });
 */
export function useStopPipelineMutation(baseOptions?: Apollo.MutationHookOptions<StopPipelineMutation, StopPipelineMutationVariables>) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useMutation<StopPipelineMutation, StopPipelineMutationVariables>(StopPipelineDocument, options);
      }
export type StopPipelineMutationHookResult = ReturnType<typeof useStopPipelineMutation>;
export type StopPipelineMutationResult = Apollo.MutationResult<StopPipelineMutation>;
export type StopPipelineMutationOptions = Apollo.BaseMutationOptions<StopPipelineMutation, StopPipelineMutationVariables>;
export const DeletePipelineVersionDocument = gql`
    mutation deletePipelineVersion($input: DeletePipelineVersionInput!) {
  deletePipelineVersion(input: $input) {
    success
    errors
  }
}
    `;
export type DeletePipelineVersionMutationFn = Apollo.MutationFunction<DeletePipelineVersionMutation, DeletePipelineVersionMutationVariables>;

/**
 * __useDeletePipelineVersionMutation__
 *
 * To run a mutation, you first call `useDeletePipelineVersionMutation` within a React component and pass it any options that fit your needs.
 * When your component renders, `useDeletePipelineVersionMutation` returns a tuple that includes:
 * - A mutate function that you can call at any time to execute the mutation
 * - An object with fields that represent the current status of the mutation's execution
 *
 * @param baseOptions options that will be passed into the mutation, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options-2;
 *
 * @example
 * const [deletePipelineVersionMutation, { data, loading, error }] = useDeletePipelineVersionMutation({
 *   variables: {
 *      input: // value for 'input'
 *   },
 * });
 */
export function useDeletePipelineVersionMutation(baseOptions?: Apollo.MutationHookOptions<DeletePipelineVersionMutation, DeletePipelineVersionMutationVariables>) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useMutation<DeletePipelineVersionMutation, DeletePipelineVersionMutationVariables>(DeletePipelineVersionDocument, options);
      }
export type DeletePipelineVersionMutationHookResult = ReturnType<typeof useDeletePipelineVersionMutation>;
export type DeletePipelineVersionMutationResult = Apollo.MutationResult<DeletePipelineVersionMutation>;
export type DeletePipelineVersionMutationOptions = Apollo.BaseMutationOptions<DeletePipelineVersionMutation, DeletePipelineVersionMutationVariables>;
export const DeletePipelineTemplateDocument = gql`
    mutation deletePipelineTemplate($input: DeletePipelineTemplateInput!) {
  deletePipelineTemplate(input: $input) {
    success
    errors
  }
}
    `;
export type DeletePipelineTemplateMutationFn = Apollo.MutationFunction<DeletePipelineTemplateMutation, DeletePipelineTemplateMutationVariables>;

/**
 * __useDeletePipelineTemplateMutation__
 *
 * To run a mutation, you first call `useDeletePipelineTemplateMutation` within a React component and pass it any options that fit your needs.
 * When your component renders, `useDeletePipelineTemplateMutation` returns a tuple that includes:
 * - A mutate function that you can call at any time to execute the mutation
 * - An object with fields that represent the current status of the mutation's execution
 *
 * @param baseOptions options that will be passed into the mutation, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options-2;
 *
 * @example
 * const [deletePipelineTemplateMutation, { data, loading, error }] = useDeletePipelineTemplateMutation({
 *   variables: {
 *      input: // value for 'input'
 *   },
 * });
 */
export function useDeletePipelineTemplateMutation(baseOptions?: Apollo.MutationHookOptions<DeletePipelineTemplateMutation, DeletePipelineTemplateMutationVariables>) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useMutation<DeletePipelineTemplateMutation, DeletePipelineTemplateMutationVariables>(DeletePipelineTemplateDocument, options);
      }
export type DeletePipelineTemplateMutationHookResult = ReturnType<typeof useDeletePipelineTemplateMutation>;
export type DeletePipelineTemplateMutationResult = Apollo.MutationResult<DeletePipelineTemplateMutation>;
export type DeletePipelineTemplateMutationOptions = Apollo.BaseMutationOptions<DeletePipelineTemplateMutation, DeletePipelineTemplateMutationVariables>;
export const JoinWorkspaceDocument = gql`
    mutation joinWorkspace($input: JoinWorkspaceInput!) {
  joinWorkspace(input: $input) {
    success
    errors
    invitation {
      id
      status
      invitedBy {
        ...User_user
      }
      role
      workspace {
        slug
        name
      }
      createdAt
    }
    workspace {
      slug
    }
  }
}
    ${User_UserFragmentDoc}`;
export type JoinWorkspaceMutationFn = Apollo.MutationFunction<JoinWorkspaceMutation, JoinWorkspaceMutationVariables>;

/**
 * __useJoinWorkspaceMutation__
 *
 * To run a mutation, you first call `useJoinWorkspaceMutation` within a React component and pass it any options that fit your needs.
 * When your component renders, `useJoinWorkspaceMutation` returns a tuple that includes:
 * - A mutate function that you can call at any time to execute the mutation
 * - An object with fields that represent the current status of the mutation's execution
 *
 * @param baseOptions options that will be passed into the mutation, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options-2;
 *
 * @example
 * const [joinWorkspaceMutation, { data, loading, error }] = useJoinWorkspaceMutation({
 *   variables: {
 *      input: // value for 'input'
 *   },
 * });
 */
export function useJoinWorkspaceMutation(baseOptions?: Apollo.MutationHookOptions<JoinWorkspaceMutation, JoinWorkspaceMutationVariables>) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useMutation<JoinWorkspaceMutation, JoinWorkspaceMutationVariables>(JoinWorkspaceDocument, options);
      }
export type JoinWorkspaceMutationHookResult = ReturnType<typeof useJoinWorkspaceMutation>;
export type JoinWorkspaceMutationResult = Apollo.MutationResult<JoinWorkspaceMutation>;
export type JoinWorkspaceMutationOptions = Apollo.BaseMutationOptions<JoinWorkspaceMutation, JoinWorkspaceMutationVariables>;
export const DeclineWorkspaceInvitationDocument = gql`
    mutation declineWorkspaceInvitation($input: DeclineWorkspaceInvitationInput!) {
  declineWorkspaceInvitation(input: $input) {
    success
    invitation {
      id
      status
    }
    errors
  }
}
    `;
export type DeclineWorkspaceInvitationMutationFn = Apollo.MutationFunction<DeclineWorkspaceInvitationMutation, DeclineWorkspaceInvitationMutationVariables>;

/**
 * __useDeclineWorkspaceInvitationMutation__
 *
 * To run a mutation, you first call `useDeclineWorkspaceInvitationMutation` within a React component and pass it any options that fit your needs.
 * When your component renders, `useDeclineWorkspaceInvitationMutation` returns a tuple that includes:
 * - A mutate function that you can call at any time to execute the mutation
 * - An object with fields that represent the current status of the mutation's execution
 *
 * @param baseOptions options that will be passed into the mutation, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options-2;
 *
 * @example
 * const [declineWorkspaceInvitationMutation, { data, loading, error }] = useDeclineWorkspaceInvitationMutation({
 *   variables: {
 *      input: // value for 'input'
 *   },
 * });
 */
export function useDeclineWorkspaceInvitationMutation(baseOptions?: Apollo.MutationHookOptions<DeclineWorkspaceInvitationMutation, DeclineWorkspaceInvitationMutationVariables>) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useMutation<DeclineWorkspaceInvitationMutation, DeclineWorkspaceInvitationMutationVariables>(DeclineWorkspaceInvitationDocument, options);
      }
export type DeclineWorkspaceInvitationMutationHookResult = ReturnType<typeof useDeclineWorkspaceInvitationMutation>;
export type DeclineWorkspaceInvitationMutationResult = Apollo.MutationResult<DeclineWorkspaceInvitationMutation>;
export type DeclineWorkspaceInvitationMutationOptions = Apollo.BaseMutationOptions<DeclineWorkspaceInvitationMutation, DeclineWorkspaceInvitationMutationVariables>;
export const DeleteWorkspaceInvitationDocument = gql`
    mutation deleteWorkspaceInvitation($input: DeleteWorkspaceInvitationInput!) {
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
    mutation resendWorkspaceInvitation($input: ResendWorkspaceInvitationInput!) {
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
export const AddPipelineRecipientDocument = gql`
    mutation addPipelineRecipient($input: CreatePipelineRecipientInput!) {
  addPipelineRecipient(input: $input) {
    success
    errors
  }
}
    `;
export type AddPipelineRecipientMutationFn = Apollo.MutationFunction<AddPipelineRecipientMutation, AddPipelineRecipientMutationVariables>;

/**
 * __useAddPipelineRecipientMutation__
 *
 * To run a mutation, you first call `useAddPipelineRecipientMutation` within a React component and pass it any options that fit your needs.
 * When your component renders, `useAddPipelineRecipientMutation` returns a tuple that includes:
 * - A mutate function that you can call at any time to execute the mutation
 * - An object with fields that represent the current status of the mutation's execution
 *
 * @param baseOptions options that will be passed into the mutation, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options-2;
 *
 * @example
 * const [addPipelineRecipientMutation, { data, loading, error }] = useAddPipelineRecipientMutation({
 *   variables: {
 *      input: // value for 'input'
 *   },
 * });
 */
export function useAddPipelineRecipientMutation(baseOptions?: Apollo.MutationHookOptions<AddPipelineRecipientMutation, AddPipelineRecipientMutationVariables>) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useMutation<AddPipelineRecipientMutation, AddPipelineRecipientMutationVariables>(AddPipelineRecipientDocument, options);
      }
export type AddPipelineRecipientMutationHookResult = ReturnType<typeof useAddPipelineRecipientMutation>;
export type AddPipelineRecipientMutationResult = Apollo.MutationResult<AddPipelineRecipientMutation>;
export type AddPipelineRecipientMutationOptions = Apollo.BaseMutationOptions<AddPipelineRecipientMutation, AddPipelineRecipientMutationVariables>;
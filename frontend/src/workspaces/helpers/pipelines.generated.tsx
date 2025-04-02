import * as Types from '../../graphql/types';

import { gql } from '@apollo/client';
import * as Apollo from '@apollo/client';
const defaultOptions = {} as const;
export type UpdateWorkspacePipelineMutationVariables = Types.Exact<{
  input: Types.UpdatePipelineInput;
}>;


export type UpdateWorkspacePipelineMutation = { __typename?: 'Mutation', updatePipeline: { __typename?: 'UpdatePipelineResult', success: boolean, errors: Array<Types.UpdatePipelineError>, pipeline?: { __typename?: 'Pipeline', id: string, name?: string | null, description?: string | null, schedule?: string | null, config: any, updatedAt?: any | null, webhookEnabled: boolean, webhookUrl?: string | null, recipients: Array<{ __typename?: 'PipelineRecipient', user: { __typename?: 'User', id: string, displayName: string } }> } | null } };

export type RunWorkspacePipelineMutationVariables = Types.Exact<{
  input: Types.RunPipelineInput;
}>;


export type RunWorkspacePipelineMutation = { __typename?: 'Mutation', runPipeline: { __typename?: 'RunPipelineResult', success: boolean, errors: Array<Types.PipelineError>, run?: { __typename?: 'PipelineRun', id: string, pipeline: { __typename: 'Pipeline', id: string } } | null } };

export type NewRunFragment = { __typename?: 'PipelineRun', id: string };

export type DeletePipelineVersionMutationVariables = Types.Exact<{
  input: Types.DeletePipelineVersionInput;
}>;


export type DeletePipelineVersionMutation = { __typename?: 'Mutation', deletePipelineVersion: { __typename?: 'DeletePipelineVersionResult', success: boolean, errors: Array<Types.DeletePipelineVersionError> } };

export type AddPipelineRecipientMutationVariables = Types.Exact<{
  input: Types.CreatePipelineRecipientInput;
}>;


export type AddPipelineRecipientMutation = { __typename?: 'Mutation', addPipelineRecipient: { __typename?: 'AddPipelineRecipientResult', success: boolean, errors: Array<Types.PipelineRecipientError> } };

export type UpdatePipelineRecipientMutationVariables = Types.Exact<{
  input: Types.UpdatePipelineRecipientInput;
}>;


export type UpdatePipelineRecipientMutation = { __typename?: 'Mutation', updatePipelineRecipient: { __typename?: 'UpdatePipelineRecipientResult', success: boolean, errors: Array<Types.PipelineRecipientError>, recipient?: { __typename?: 'PipelineRecipient', id: string, notificationLevel: Types.PipelineNotificationLevel } | null } };

export type DeletePipelineRecipientMutationVariables = Types.Exact<{
  input: Types.DeletePipelineRecipientInput;
}>;


export type DeletePipelineRecipientMutation = { __typename?: 'Mutation', deletePipelineRecipient: { __typename?: 'DeletePipelineRecipientResult', success: boolean, errors: Array<Types.PipelineRecipientError> } };

export const NewRunFragmentDoc = gql`
    fragment NewRun on PipelineRun {
  id
}
    `;
export const UpdateWorkspacePipelineDocument = gql`
    mutation UpdateWorkspacePipeline($input: UpdatePipelineInput!) {
  updatePipeline(input: $input) {
    success
    errors
    pipeline {
      id
      name
      description
      schedule
      config
      updatedAt
      webhookEnabled
      webhookUrl
      recipients {
        user {
          id
          displayName
        }
      }
    }
  }
}
    `;
export type UpdateWorkspacePipelineMutationFn = Apollo.MutationFunction<UpdateWorkspacePipelineMutation, UpdateWorkspacePipelineMutationVariables>;

/**
 * __useUpdateWorkspacePipelineMutation__
 *
 * To run a mutation, you first call `useUpdateWorkspacePipelineMutation` within a React component and pass it any options that fit your needs.
 * When your component renders, `useUpdateWorkspacePipelineMutation` returns a tuple that includes:
 * - A mutate function that you can call at any time to execute the mutation
 * - An object with fields that represent the current status of the mutation's execution
 *
 * @param baseOptions options that will be passed into the mutation, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options-2;
 *
 * @example
 * const [updateWorkspacePipelineMutation, { data, loading, error }] = useUpdateWorkspacePipelineMutation({
 *   variables: {
 *      input: // value for 'input'
 *   },
 * });
 */
export function useUpdateWorkspacePipelineMutation(baseOptions?: Apollo.MutationHookOptions<UpdateWorkspacePipelineMutation, UpdateWorkspacePipelineMutationVariables>) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useMutation<UpdateWorkspacePipelineMutation, UpdateWorkspacePipelineMutationVariables>(UpdateWorkspacePipelineDocument, options);
      }
export type UpdateWorkspacePipelineMutationHookResult = ReturnType<typeof useUpdateWorkspacePipelineMutation>;
export type UpdateWorkspacePipelineMutationResult = Apollo.MutationResult<UpdateWorkspacePipelineMutation>;
export type UpdateWorkspacePipelineMutationOptions = Apollo.BaseMutationOptions<UpdateWorkspacePipelineMutation, UpdateWorkspacePipelineMutationVariables>;
export const RunWorkspacePipelineDocument = gql`
    mutation RunWorkspacePipeline($input: RunPipelineInput!) {
  runPipeline(input: $input) {
    success
    errors
    run {
      id
      pipeline {
        __typename
        id
      }
    }
  }
}
    `;
export type RunWorkspacePipelineMutationFn = Apollo.MutationFunction<RunWorkspacePipelineMutation, RunWorkspacePipelineMutationVariables>;

/**
 * __useRunWorkspacePipelineMutation__
 *
 * To run a mutation, you first call `useRunWorkspacePipelineMutation` within a React component and pass it any options that fit your needs.
 * When your component renders, `useRunWorkspacePipelineMutation` returns a tuple that includes:
 * - A mutate function that you can call at any time to execute the mutation
 * - An object with fields that represent the current status of the mutation's execution
 *
 * @param baseOptions options that will be passed into the mutation, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options-2;
 *
 * @example
 * const [runWorkspacePipelineMutation, { data, loading, error }] = useRunWorkspacePipelineMutation({
 *   variables: {
 *      input: // value for 'input'
 *   },
 * });
 */
export function useRunWorkspacePipelineMutation(baseOptions?: Apollo.MutationHookOptions<RunWorkspacePipelineMutation, RunWorkspacePipelineMutationVariables>) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useMutation<RunWorkspacePipelineMutation, RunWorkspacePipelineMutationVariables>(RunWorkspacePipelineDocument, options);
      }
export type RunWorkspacePipelineMutationHookResult = ReturnType<typeof useRunWorkspacePipelineMutation>;
export type RunWorkspacePipelineMutationResult = Apollo.MutationResult<RunWorkspacePipelineMutation>;
export type RunWorkspacePipelineMutationOptions = Apollo.BaseMutationOptions<RunWorkspacePipelineMutation, RunWorkspacePipelineMutationVariables>;
export const DeletePipelineVersionDocument = gql`
    mutation DeletePipelineVersion($input: DeletePipelineVersionInput!) {
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
export const UpdatePipelineRecipientDocument = gql`
    mutation updatePipelineRecipient($input: UpdatePipelineRecipientInput!) {
  updatePipelineRecipient(input: $input) {
    success
    errors
    recipient {
      id
      notificationLevel
    }
  }
}
    `;
export type UpdatePipelineRecipientMutationFn = Apollo.MutationFunction<UpdatePipelineRecipientMutation, UpdatePipelineRecipientMutationVariables>;

/**
 * __useUpdatePipelineRecipientMutation__
 *
 * To run a mutation, you first call `useUpdatePipelineRecipientMutation` within a React component and pass it any options that fit your needs.
 * When your component renders, `useUpdatePipelineRecipientMutation` returns a tuple that includes:
 * - A mutate function that you can call at any time to execute the mutation
 * - An object with fields that represent the current status of the mutation's execution
 *
 * @param baseOptions options that will be passed into the mutation, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options-2;
 *
 * @example
 * const [updatePipelineRecipientMutation, { data, loading, error }] = useUpdatePipelineRecipientMutation({
 *   variables: {
 *      input: // value for 'input'
 *   },
 * });
 */
export function useUpdatePipelineRecipientMutation(baseOptions?: Apollo.MutationHookOptions<UpdatePipelineRecipientMutation, UpdatePipelineRecipientMutationVariables>) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useMutation<UpdatePipelineRecipientMutation, UpdatePipelineRecipientMutationVariables>(UpdatePipelineRecipientDocument, options);
      }
export type UpdatePipelineRecipientMutationHookResult = ReturnType<typeof useUpdatePipelineRecipientMutation>;
export type UpdatePipelineRecipientMutationResult = Apollo.MutationResult<UpdatePipelineRecipientMutation>;
export type UpdatePipelineRecipientMutationOptions = Apollo.BaseMutationOptions<UpdatePipelineRecipientMutation, UpdatePipelineRecipientMutationVariables>;
export const DeletePipelineRecipientDocument = gql`
    mutation deletePipelineRecipient($input: DeletePipelineRecipientInput!) {
  deletePipelineRecipient(input: $input) {
    success
    errors
  }
}
    `;
export type DeletePipelineRecipientMutationFn = Apollo.MutationFunction<DeletePipelineRecipientMutation, DeletePipelineRecipientMutationVariables>;

/**
 * __useDeletePipelineRecipientMutation__
 *
 * To run a mutation, you first call `useDeletePipelineRecipientMutation` within a React component and pass it any options that fit your needs.
 * When your component renders, `useDeletePipelineRecipientMutation` returns a tuple that includes:
 * - A mutate function that you can call at any time to execute the mutation
 * - An object with fields that represent the current status of the mutation's execution
 *
 * @param baseOptions options that will be passed into the mutation, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options-2;
 *
 * @example
 * const [deletePipelineRecipientMutation, { data, loading, error }] = useDeletePipelineRecipientMutation({
 *   variables: {
 *      input: // value for 'input'
 *   },
 * });
 */
export function useDeletePipelineRecipientMutation(baseOptions?: Apollo.MutationHookOptions<DeletePipelineRecipientMutation, DeletePipelineRecipientMutationVariables>) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useMutation<DeletePipelineRecipientMutation, DeletePipelineRecipientMutationVariables>(DeletePipelineRecipientDocument, options);
      }
export type DeletePipelineRecipientMutationHookResult = ReturnType<typeof useDeletePipelineRecipientMutation>;
export type DeletePipelineRecipientMutationResult = Apollo.MutationResult<DeletePipelineRecipientMutation>;
export type DeletePipelineRecipientMutationOptions = Apollo.BaseMutationOptions<DeletePipelineRecipientMutation, DeletePipelineRecipientMutationVariables>;
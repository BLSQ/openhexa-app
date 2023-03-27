import * as Types from '../../graphql-types';

import { gql } from '@apollo/client';
import * as Apollo from '@apollo/client';
const defaultOptions = {} as const;
export type UpdateWorkspacePipelineMutationVariables = Types.Exact<{
  input: Types.UpdatePipelineInput;
}>;


export type UpdateWorkspacePipelineMutation = { __typename?: 'Mutation', updatePipeline: { __typename?: 'UpdatePipelineResult', success: boolean, errors: Array<Types.UpdatePipelineError>, pipeline?: { __typename?: 'Pipeline', id: string, name: string, description?: string | null, schedule?: string | null, config: any, updatedAt?: any | null } | null } };

export type RunWorkspacePipelineMutationVariables = Types.Exact<{
  input: Types.RunPipelineInput;
}>;


export type RunWorkspacePipelineMutation = { __typename?: 'Mutation', runPipeline: { __typename?: 'RunPipelineResult', success: boolean, errors: Array<Types.PipelineError>, run?: { __typename?: 'PipelineRun', id: string } | null } };


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
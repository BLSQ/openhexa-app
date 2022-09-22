import * as Types from '../../graphql-types';

import { gql } from '@apollo/client';
import * as Apollo from '@apollo/client';
const defaultOptions = {} as const;
export type UpdatePipelineMutationVariables = Types.Exact<{
  input: Types.UpdateDagInput;
}>;


export type UpdatePipelineMutation = { __typename?: 'Mutation', updateDAG: { __typename?: 'UpdateDAGResult', success: boolean, errors: Array<Types.UpdateDagError>, dag?: { __typename?: 'DAG', id: string, label: string, description?: string | null, schedule?: string | null } | null } };


export const UpdatePipelineDocument = gql`
    mutation UpdatePipeline($input: UpdateDAGInput!) {
  updateDAG(input: $input) {
    success
    errors
    dag {
      id
      label
      description
      schedule
    }
  }
}
    `;
export type UpdatePipelineMutationFn = Apollo.MutationFunction<UpdatePipelineMutation, UpdatePipelineMutationVariables>;

/**
 * __useUpdatePipelineMutation__
 *
 * To run a mutation, you first call `useUpdatePipelineMutation` within a React component and pass it any options that fit your needs.
 * When your component renders, `useUpdatePipelineMutation` returns a tuple that includes:
 * - A mutate function that you can call at any time to execute the mutation
 * - An object with fields that represent the current status of the mutation's execution
 *
 * @param baseOptions options that will be passed into the mutation, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options-2;
 *
 * @example
 * const [updatePipelineMutation, { data, loading, error }] = useUpdatePipelineMutation({
 *   variables: {
 *      input: // value for 'input'
 *   },
 * });
 */
export function useUpdatePipelineMutation(baseOptions?: Apollo.MutationHookOptions<UpdatePipelineMutation, UpdatePipelineMutationVariables>) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useMutation<UpdatePipelineMutation, UpdatePipelineMutationVariables>(UpdatePipelineDocument, options);
      }
export type UpdatePipelineMutationHookResult = ReturnType<typeof useUpdatePipelineMutation>;
export type UpdatePipelineMutationResult = Apollo.MutationResult<UpdatePipelineMutation>;
export type UpdatePipelineMutationOptions = Apollo.BaseMutationOptions<UpdatePipelineMutation, UpdatePipelineMutationVariables>;
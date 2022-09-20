import * as Types from '../../graphql-types';

import { gql } from '@apollo/client';
import * as Apollo from '@apollo/client';
const defaultOptions = {} as const;
export type RunPipelineMutationVariables = Types.Exact<{
  input: Types.RunDagInput;
}>;


export type RunPipelineMutation = { __typename?: 'Mutation', runDAG: { __typename?: 'RunDAGResult', success: boolean, errors: Array<Types.RunDagError>, dag?: { __typename?: 'DAG', id: string } | null, dagRun?: { __typename?: 'DAGRun', id: string, externalUrl?: any | null, externalId?: string | null } | null } };


export const RunPipelineDocument = gql`
    mutation RunPipeline($input: RunDAGInput!) {
  runDAG(input: $input) {
    success
    errors
    dag {
      id
    }
    dagRun {
      id
      externalUrl
      externalId
    }
  }
}
    `;
export type RunPipelineMutationFn = Apollo.MutationFunction<RunPipelineMutation, RunPipelineMutationVariables>;

/**
 * __useRunPipelineMutation__
 *
 * To run a mutation, you first call `useRunPipelineMutation` within a React component and pass it any options that fit your needs.
 * When your component renders, `useRunPipelineMutation` returns a tuple that includes:
 * - A mutate function that you can call at any time to execute the mutation
 * - An object with fields that represent the current status of the mutation's execution
 *
 * @param baseOptions options that will be passed into the mutation, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options-2;
 *
 * @example
 * const [runPipelineMutation, { data, loading, error }] = useRunPipelineMutation({
 *   variables: {
 *      input: // value for 'input'
 *   },
 * });
 */
export function useRunPipelineMutation(baseOptions?: Apollo.MutationHookOptions<RunPipelineMutation, RunPipelineMutationVariables>) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useMutation<RunPipelineMutation, RunPipelineMutationVariables>(RunPipelineDocument, options);
      }
export type RunPipelineMutationHookResult = ReturnType<typeof useRunPipelineMutation>;
export type RunPipelineMutationResult = Apollo.MutationResult<RunPipelineMutation>;
export type RunPipelineMutationOptions = Apollo.BaseMutationOptions<RunPipelineMutation, RunPipelineMutationVariables>;
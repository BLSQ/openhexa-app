import * as Types from '../../graphql/types';

import { gql } from '@apollo/client';
import * as Apollo from '@apollo/client';
const defaultOptions = {} as const;
export type RunPipelineMutationVariables = Types.Exact<{
  input: Types.RunDagInput;
}>;


export type RunPipelineMutation = { __typename?: 'Mutation', runDAG: { __typename?: 'RunDAGResult', success: boolean, errors: Array<Types.RunDagError>, dag?: { __typename?: 'DAG', id: string } | null, dagRun?: { __typename?: 'DAGRun', id: string, externalUrl?: any | null, externalId?: string | null } | null } };

export type GetPipelineVersionQueryVariables = Types.Exact<{
  versionId: Types.Scalars['UUID']['input'];
}>;


export type GetPipelineVersionQuery = { __typename?: 'Query', pipelineVersion?: { __typename?: 'PipelineVersion', id: string, versionName: string, zipfile: string, pipeline: { __typename?: 'Pipeline', code: string } } | null };


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
export const GetPipelineVersionDocument = gql`
    query GetPipelineVersion($versionId: UUID!) {
  pipelineVersion(id: $versionId) {
    id
    versionName
    pipeline {
      code
    }
    zipfile
  }
}
    `;

/**
 * __useGetPipelineVersionQuery__
 *
 * To run a query within a React component, call `useGetPipelineVersionQuery` and pass it any options that fit your needs.
 * When your component renders, `useGetPipelineVersionQuery` returns an object from Apollo Client that contains loading, error, and data properties
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = useGetPipelineVersionQuery({
 *   variables: {
 *      versionId: // value for 'versionId'
 *   },
 * });
 */
export function useGetPipelineVersionQuery(baseOptions: Apollo.QueryHookOptions<GetPipelineVersionQuery, GetPipelineVersionQueryVariables> & ({ variables: GetPipelineVersionQueryVariables; skip?: boolean; } | { skip: boolean; }) ) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useQuery<GetPipelineVersionQuery, GetPipelineVersionQueryVariables>(GetPipelineVersionDocument, options);
      }
export function useGetPipelineVersionLazyQuery(baseOptions?: Apollo.LazyQueryHookOptions<GetPipelineVersionQuery, GetPipelineVersionQueryVariables>) {
          const options = {...defaultOptions, ...baseOptions}
          return Apollo.useLazyQuery<GetPipelineVersionQuery, GetPipelineVersionQueryVariables>(GetPipelineVersionDocument, options);
        }
export function useGetPipelineVersionSuspenseQuery(baseOptions?: Apollo.SkipToken | Apollo.SuspenseQueryHookOptions<GetPipelineVersionQuery, GetPipelineVersionQueryVariables>) {
          const options = baseOptions === Apollo.skipToken ? baseOptions : {...defaultOptions, ...baseOptions}
          return Apollo.useSuspenseQuery<GetPipelineVersionQuery, GetPipelineVersionQueryVariables>(GetPipelineVersionDocument, options);
        }
export type GetPipelineVersionQueryHookResult = ReturnType<typeof useGetPipelineVersionQuery>;
export type GetPipelineVersionLazyQueryHookResult = ReturnType<typeof useGetPipelineVersionLazyQuery>;
export type GetPipelineVersionSuspenseQueryHookResult = ReturnType<typeof useGetPipelineVersionSuspenseQuery>;
export type GetPipelineVersionQueryResult = Apollo.QueryResult<GetPipelineVersionQuery, GetPipelineVersionQueryVariables>;
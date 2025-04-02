import * as Types from '../../graphql/types';

import { gql } from '@apollo/client';
import * as Apollo from '@apollo/client';
const defaultOptions = {} as const;
export type GetPipelineRunQueryVariables = Types.Exact<{
  runId: Types.Scalars['UUID']['input'];
}>;


export type GetPipelineRunQuery = { __typename?: 'Query', dagRun?: { __typename?: 'DAGRun', config?: any | null, externalUrl?: any | null, externalId?: string | null, status: Types.DagRunStatus, executionDate?: any | null, duration?: number | null } | null };

export type GetRunOutputDownloadUrlMutationVariables = Types.Exact<{
  input: Types.PrepareDownloadUrlInput;
}>;


export type GetRunOutputDownloadUrlMutation = { __typename?: 'Mutation', prepareDownloadURL?: { __typename?: 'PrepareDownloadURLResult', success: boolean, url?: any | null } | null };


export const GetPipelineRunDocument = gql`
    query GetPipelineRun($runId: UUID!) {
  dagRun(id: $runId) {
    config
    externalUrl
    externalId
    status
    executionDate
    duration
  }
}
    `;

/**
 * __useGetPipelineRunQuery__
 *
 * To run a query within a React component, call `useGetPipelineRunQuery` and pass it any options that fit your needs.
 * When your component renders, `useGetPipelineRunQuery` returns an object from Apollo Client that contains loading, error, and data properties
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = useGetPipelineRunQuery({
 *   variables: {
 *      runId: // value for 'runId'
 *   },
 * });
 */
export function useGetPipelineRunQuery(baseOptions: Apollo.QueryHookOptions<GetPipelineRunQuery, GetPipelineRunQueryVariables> & ({ variables: GetPipelineRunQueryVariables; skip?: boolean; } | { skip: boolean; }) ) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useQuery<GetPipelineRunQuery, GetPipelineRunQueryVariables>(GetPipelineRunDocument, options);
      }
export function useGetPipelineRunLazyQuery(baseOptions?: Apollo.LazyQueryHookOptions<GetPipelineRunQuery, GetPipelineRunQueryVariables>) {
          const options = {...defaultOptions, ...baseOptions}
          return Apollo.useLazyQuery<GetPipelineRunQuery, GetPipelineRunQueryVariables>(GetPipelineRunDocument, options);
        }
export function useGetPipelineRunSuspenseQuery(baseOptions?: Apollo.SkipToken | Apollo.SuspenseQueryHookOptions<GetPipelineRunQuery, GetPipelineRunQueryVariables>) {
          const options = baseOptions === Apollo.skipToken ? baseOptions : {...defaultOptions, ...baseOptions}
          return Apollo.useSuspenseQuery<GetPipelineRunQuery, GetPipelineRunQueryVariables>(GetPipelineRunDocument, options);
        }
export type GetPipelineRunQueryHookResult = ReturnType<typeof useGetPipelineRunQuery>;
export type GetPipelineRunLazyQueryHookResult = ReturnType<typeof useGetPipelineRunLazyQuery>;
export type GetPipelineRunSuspenseQueryHookResult = ReturnType<typeof useGetPipelineRunSuspenseQuery>;
export type GetPipelineRunQueryResult = Apollo.QueryResult<GetPipelineRunQuery, GetPipelineRunQueryVariables>;
export const GetRunOutputDownloadUrlDocument = gql`
    mutation GetRunOutputDownloadURL($input: PrepareDownloadURLInput!) {
  prepareDownloadURL(input: $input) {
    success
    url
  }
}
    `;
export type GetRunOutputDownloadUrlMutationFn = Apollo.MutationFunction<GetRunOutputDownloadUrlMutation, GetRunOutputDownloadUrlMutationVariables>;

/**
 * __useGetRunOutputDownloadUrlMutation__
 *
 * To run a mutation, you first call `useGetRunOutputDownloadUrlMutation` within a React component and pass it any options that fit your needs.
 * When your component renders, `useGetRunOutputDownloadUrlMutation` returns a tuple that includes:
 * - A mutate function that you can call at any time to execute the mutation
 * - An object with fields that represent the current status of the mutation's execution
 *
 * @param baseOptions options that will be passed into the mutation, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options-2;
 *
 * @example
 * const [getRunOutputDownloadUrlMutation, { data, loading, error }] = useGetRunOutputDownloadUrlMutation({
 *   variables: {
 *      input: // value for 'input'
 *   },
 * });
 */
export function useGetRunOutputDownloadUrlMutation(baseOptions?: Apollo.MutationHookOptions<GetRunOutputDownloadUrlMutation, GetRunOutputDownloadUrlMutationVariables>) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useMutation<GetRunOutputDownloadUrlMutation, GetRunOutputDownloadUrlMutationVariables>(GetRunOutputDownloadUrlDocument, options);
      }
export type GetRunOutputDownloadUrlMutationHookResult = ReturnType<typeof useGetRunOutputDownloadUrlMutation>;
export type GetRunOutputDownloadUrlMutationResult = Apollo.MutationResult<GetRunOutputDownloadUrlMutation>;
export type GetRunOutputDownloadUrlMutationOptions = Apollo.BaseMutationOptions<GetRunOutputDownloadUrlMutation, GetRunOutputDownloadUrlMutationVariables>;
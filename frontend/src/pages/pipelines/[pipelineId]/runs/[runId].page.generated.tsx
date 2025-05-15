import * as Types from '../../../../graphql/types';

import { gql } from '@apollo/client';
import { PipelineRunDataCard_DagRunFragmentDoc, PipelineRunDataCard_DagFragmentDoc } from '../../../../pipelines/features/PipelineRunDataCard/PipelineRunDataCard.generated';
import * as Apollo from '@apollo/client';
const defaultOptions = {} as const;
export type PipelineRunPageQueryVariables = Types.Exact<{
  pipelineId: Types.Scalars['UUID']['input'];
  runId: Types.Scalars['UUID']['input'];
}>;


export type PipelineRunPageQuery = { __typename?: 'Query', dagRun?: { __typename?: 'DAGRun', id: string, label?: string | null, triggerMode?: Types.DagRunTrigger | null, externalId?: string | null, externalUrl?: any | null, executionDate?: any | null, status: Types.DagRunStatus, config?: any | null, duration?: number | null, progress: number, logs?: string | null, isFavorite: boolean, user?: { __typename?: 'User', displayName: string, id: string, email: string, avatar: { __typename?: 'Avatar', initials: string, color: string } } | null, outputs: Array<{ __typename?: 'DAGRunOutput', title: string, uri: string }>, messages: Array<{ __typename: 'DAGRunMessage', message: string, timestamp?: any | null, priority: string }> } | null, dag?: { __typename?: 'DAG', id: string, externalId: string, label: string, formCode?: string | null } | null };


export const PipelineRunPageDocument = gql`
    query PipelineRunPage($pipelineId: UUID!, $runId: UUID!) {
  dagRun(id: $runId) {
    id
    label
    triggerMode
    user {
      displayName
    }
    ...PipelineRunDataCard_dagRun
  }
  dag(id: $pipelineId) {
    id
    externalId
    label
    ...PipelineRunDataCard_dag
  }
}
    ${PipelineRunDataCard_DagRunFragmentDoc}
${PipelineRunDataCard_DagFragmentDoc}`;

/**
 * __usePipelineRunPageQuery__
 *
 * To run a query within a React component, call `usePipelineRunPageQuery` and pass it any options that fit your needs.
 * When your component renders, `usePipelineRunPageQuery` returns an object from Apollo Client that contains loading, error, and data properties
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = usePipelineRunPageQuery({
 *   variables: {
 *      pipelineId: // value for 'pipelineId'
 *      runId: // value for 'runId'
 *   },
 * });
 */
export function usePipelineRunPageQuery(baseOptions: Apollo.QueryHookOptions<PipelineRunPageQuery, PipelineRunPageQueryVariables> & ({ variables: PipelineRunPageQueryVariables; skip?: boolean; } | { skip: boolean; }) ) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useQuery<PipelineRunPageQuery, PipelineRunPageQueryVariables>(PipelineRunPageDocument, options);
      }
export function usePipelineRunPageLazyQuery(baseOptions?: Apollo.LazyQueryHookOptions<PipelineRunPageQuery, PipelineRunPageQueryVariables>) {
          const options = {...defaultOptions, ...baseOptions}
          return Apollo.useLazyQuery<PipelineRunPageQuery, PipelineRunPageQueryVariables>(PipelineRunPageDocument, options);
        }
export function usePipelineRunPageSuspenseQuery(baseOptions?: Apollo.SkipToken | Apollo.SuspenseQueryHookOptions<PipelineRunPageQuery, PipelineRunPageQueryVariables>) {
          const options = baseOptions === Apollo.skipToken ? baseOptions : {...defaultOptions, ...baseOptions}
          return Apollo.useSuspenseQuery<PipelineRunPageQuery, PipelineRunPageQueryVariables>(PipelineRunPageDocument, options);
        }
export type PipelineRunPageQueryHookResult = ReturnType<typeof usePipelineRunPageQuery>;
export type PipelineRunPageLazyQueryHookResult = ReturnType<typeof usePipelineRunPageLazyQuery>;
export type PipelineRunPageSuspenseQueryHookResult = ReturnType<typeof usePipelineRunPageSuspenseQuery>;
export type PipelineRunPageQueryResult = Apollo.QueryResult<PipelineRunPageQuery, PipelineRunPageQueryVariables>;
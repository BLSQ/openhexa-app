import * as Types from '../../../graphql/types';

import { gql } from '@apollo/client';
import * as Apollo from '@apollo/client';
const defaultOptions = {} as const;
export type PipelineRunPollerQueryVariables = Types.Exact<{
  runId: Types.Scalars['UUID']['input'];
}>;


export type PipelineRunPollerQuery = { __typename?: 'Query', run?: { __typename?: 'PipelineRun', duration?: number | null, progress: number, id: string, status: Types.PipelineRunStatus } | null };

export type UsePipelineRunPoller_RunFragment = { __typename?: 'PipelineRun', id: string, status: Types.PipelineRunStatus };

export const UsePipelineRunPoller_RunFragmentDoc = gql`
    fragment usePipelineRunPoller_run on PipelineRun {
  id
  status
}
    `;
export const PipelineRunPollerDocument = gql`
    query PipelineRunPoller($runId: UUID!) {
  run: pipelineRun(id: $runId) {
    ...usePipelineRunPoller_run
    duration
    progress
  }
}
    ${UsePipelineRunPoller_RunFragmentDoc}`;

/**
 * __usePipelineRunPollerQuery__
 *
 * To run a query within a React component, call `usePipelineRunPollerQuery` and pass it any options that fit your needs.
 * When your component renders, `usePipelineRunPollerQuery` returns an object from Apollo Client that contains loading, error, and data properties
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = usePipelineRunPollerQuery({
 *   variables: {
 *      runId: // value for 'runId'
 *   },
 * });
 */
export function usePipelineRunPollerQuery(baseOptions: Apollo.QueryHookOptions<PipelineRunPollerQuery, PipelineRunPollerQueryVariables> & ({ variables: PipelineRunPollerQueryVariables; skip?: boolean; } | { skip: boolean; }) ) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useQuery<PipelineRunPollerQuery, PipelineRunPollerQueryVariables>(PipelineRunPollerDocument, options);
      }
export function usePipelineRunPollerLazyQuery(baseOptions?: Apollo.LazyQueryHookOptions<PipelineRunPollerQuery, PipelineRunPollerQueryVariables>) {
          const options = {...defaultOptions, ...baseOptions}
          return Apollo.useLazyQuery<PipelineRunPollerQuery, PipelineRunPollerQueryVariables>(PipelineRunPollerDocument, options);
        }
export function usePipelineRunPollerSuspenseQuery(baseOptions?: Apollo.SkipToken | Apollo.SuspenseQueryHookOptions<PipelineRunPollerQuery, PipelineRunPollerQueryVariables>) {
          const options = baseOptions === Apollo.skipToken ? baseOptions : {...defaultOptions, ...baseOptions}
          return Apollo.useSuspenseQuery<PipelineRunPollerQuery, PipelineRunPollerQueryVariables>(PipelineRunPollerDocument, options);
        }
export type PipelineRunPollerQueryHookResult = ReturnType<typeof usePipelineRunPollerQuery>;
export type PipelineRunPollerLazyQueryHookResult = ReturnType<typeof usePipelineRunPollerLazyQuery>;
export type PipelineRunPollerSuspenseQueryHookResult = ReturnType<typeof usePipelineRunPollerSuspenseQuery>;
export type PipelineRunPollerQueryResult = Apollo.QueryResult<PipelineRunPollerQuery, PipelineRunPollerQueryVariables>;
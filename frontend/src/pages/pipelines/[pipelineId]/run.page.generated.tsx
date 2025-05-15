import * as Types from '../../../graphql/types';

import { gql } from '@apollo/client';
import { PipelineRunForm_DagFragmentDoc } from '../../../pipelines/features/PipelineRunForm/PipelineRunForm.generated';
import * as Apollo from '@apollo/client';
const defaultOptions = {} as const;
export type PipelineConfigureRunPageQueryVariables = Types.Exact<{
  pipelineId: Types.Scalars['UUID']['input'];
}>;


export type PipelineConfigureRunPageQuery = { __typename?: 'Query', dag?: { __typename?: 'DAG', id: string, label: string, externalId: string, description?: string | null, formCode?: string | null, template: { __typename?: 'DAGTemplate', sampleConfig?: any | null, description?: string | null } } | null };


export const PipelineConfigureRunPageDocument = gql`
    query PipelineConfigureRunPage($pipelineId: UUID!) {
  dag(id: $pipelineId) {
    id
    label
    externalId
    template {
      sampleConfig
      description
    }
    description
    ...PipelineRunForm_dag
  }
}
    ${PipelineRunForm_DagFragmentDoc}`;

/**
 * __usePipelineConfigureRunPageQuery__
 *
 * To run a query within a React component, call `usePipelineConfigureRunPageQuery` and pass it any options that fit your needs.
 * When your component renders, `usePipelineConfigureRunPageQuery` returns an object from Apollo Client that contains loading, error, and data properties
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = usePipelineConfigureRunPageQuery({
 *   variables: {
 *      pipelineId: // value for 'pipelineId'
 *   },
 * });
 */
export function usePipelineConfigureRunPageQuery(baseOptions: Apollo.QueryHookOptions<PipelineConfigureRunPageQuery, PipelineConfigureRunPageQueryVariables> & ({ variables: PipelineConfigureRunPageQueryVariables; skip?: boolean; } | { skip: boolean; }) ) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useQuery<PipelineConfigureRunPageQuery, PipelineConfigureRunPageQueryVariables>(PipelineConfigureRunPageDocument, options);
      }
export function usePipelineConfigureRunPageLazyQuery(baseOptions?: Apollo.LazyQueryHookOptions<PipelineConfigureRunPageQuery, PipelineConfigureRunPageQueryVariables>) {
          const options = {...defaultOptions, ...baseOptions}
          return Apollo.useLazyQuery<PipelineConfigureRunPageQuery, PipelineConfigureRunPageQueryVariables>(PipelineConfigureRunPageDocument, options);
        }
export function usePipelineConfigureRunPageSuspenseQuery(baseOptions?: Apollo.SkipToken | Apollo.SuspenseQueryHookOptions<PipelineConfigureRunPageQuery, PipelineConfigureRunPageQueryVariables>) {
          const options = baseOptions === Apollo.skipToken ? baseOptions : {...defaultOptions, ...baseOptions}
          return Apollo.useSuspenseQuery<PipelineConfigureRunPageQuery, PipelineConfigureRunPageQueryVariables>(PipelineConfigureRunPageDocument, options);
        }
export type PipelineConfigureRunPageQueryHookResult = ReturnType<typeof usePipelineConfigureRunPageQuery>;
export type PipelineConfigureRunPageLazyQueryHookResult = ReturnType<typeof usePipelineConfigureRunPageLazyQuery>;
export type PipelineConfigureRunPageSuspenseQueryHookResult = ReturnType<typeof usePipelineConfigureRunPageSuspenseQuery>;
export type PipelineConfigureRunPageQueryResult = Apollo.QueryResult<PipelineConfigureRunPageQuery, PipelineConfigureRunPageQueryVariables>;
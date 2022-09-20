import * as Types from '../../graphql-types';

import { gql } from '@apollo/client';
import * as Apollo from '@apollo/client';
const defaultOptions = {} as const;
export type GetPipelineRunQueryVariables = Types.Exact<{
  runId: Types.Scalars['String'];
}>;


export type GetPipelineRunQuery = { __typename?: 'Query', dagRun?: { __typename?: 'DAGRun', config?: any | null, externalUrl?: any | null, externalId?: string | null, status: Types.DagRunStatus, executionDate?: any | null, duration?: number | null } | null };


export const GetPipelineRunDocument = gql`
    query GetPipelineRun($runId: String!) {
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
export function useGetPipelineRunQuery(baseOptions: Apollo.QueryHookOptions<GetPipelineRunQuery, GetPipelineRunQueryVariables>) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useQuery<GetPipelineRunQuery, GetPipelineRunQueryVariables>(GetPipelineRunDocument, options);
      }
export function useGetPipelineRunLazyQuery(baseOptions?: Apollo.LazyQueryHookOptions<GetPipelineRunQuery, GetPipelineRunQueryVariables>) {
          const options = {...defaultOptions, ...baseOptions}
          return Apollo.useLazyQuery<GetPipelineRunQuery, GetPipelineRunQueryVariables>(GetPipelineRunDocument, options);
        }
export type GetPipelineRunQueryHookResult = ReturnType<typeof useGetPipelineRunQuery>;
export type GetPipelineRunLazyQueryHookResult = ReturnType<typeof useGetPipelineRunLazyQuery>;
export type GetPipelineRunQueryResult = Apollo.QueryResult<GetPipelineRunQuery, GetPipelineRunQueryVariables>;
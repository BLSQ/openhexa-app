import * as Types from '../../../graphql/types';

import { gql } from '@apollo/client';
import * as Apollo from '@apollo/client';
const defaultOptions = {} as const;
export type GetPipelineParameterChoicesQueryVariables = Types.Exact<{
  workspaceSlug: Types.Scalars['String']['input'];
  pipelineVersionId: Types.Scalars['UUID']['input'];
  parameterCode: Types.Scalars['String']['input'];
}>;


export type GetPipelineParameterChoicesQuery = { __typename?: 'Query', pipelineParameterChoices?: Array<string> | null };


export const GetPipelineParameterChoicesDocument = gql`
    query getPipelineParameterChoices($workspaceSlug: String!, $pipelineVersionId: UUID!, $parameterCode: String!) {
  pipelineParameterChoices(
    workspaceSlug: $workspaceSlug
    pipelineVersionId: $pipelineVersionId
    parameterCode: $parameterCode
  )
}
    `;

/**
 * __useGetPipelineParameterChoicesQuery__
 *
 * To run a query within a React component, call `useGetPipelineParameterChoicesQuery` and pass it any options that fit your needs.
 * When your component renders, `useGetPipelineParameterChoicesQuery` returns an object from Apollo Client that contains loading, error, and data properties
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = useGetPipelineParameterChoicesQuery({
 *   variables: {
 *      workspaceSlug: // value for 'workspaceSlug'
 *      pipelineVersionId: // value for 'pipelineVersionId'
 *      parameterCode: // value for 'parameterCode'
 *   },
 * });
 */
export function useGetPipelineParameterChoicesQuery(baseOptions: Apollo.QueryHookOptions<GetPipelineParameterChoicesQuery, GetPipelineParameterChoicesQueryVariables> & ({ variables: GetPipelineParameterChoicesQueryVariables; skip?: boolean; } | { skip: boolean; }) ) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useQuery<GetPipelineParameterChoicesQuery, GetPipelineParameterChoicesQueryVariables>(GetPipelineParameterChoicesDocument, options);
      }
export function useGetPipelineParameterChoicesLazyQuery(baseOptions?: Apollo.LazyQueryHookOptions<GetPipelineParameterChoicesQuery, GetPipelineParameterChoicesQueryVariables>) {
          const options = {...defaultOptions, ...baseOptions}
          return Apollo.useLazyQuery<GetPipelineParameterChoicesQuery, GetPipelineParameterChoicesQueryVariables>(GetPipelineParameterChoicesDocument, options);
        }
export function useGetPipelineParameterChoicesSuspenseQuery(baseOptions?: Apollo.SkipToken | Apollo.SuspenseQueryHookOptions<GetPipelineParameterChoicesQuery, GetPipelineParameterChoicesQueryVariables>) {
          const options = baseOptions === Apollo.skipToken ? baseOptions : {...defaultOptions, ...baseOptions}
          return Apollo.useSuspenseQuery<GetPipelineParameterChoicesQuery, GetPipelineParameterChoicesQueryVariables>(GetPipelineParameterChoicesDocument, options);
        }
export type GetPipelineParameterChoicesQueryHookResult = ReturnType<typeof useGetPipelineParameterChoicesQuery>;
export type GetPipelineParameterChoicesLazyQueryHookResult = ReturnType<typeof useGetPipelineParameterChoicesLazyQuery>;
export type GetPipelineParameterChoicesSuspenseQueryHookResult = ReturnType<typeof useGetPipelineParameterChoicesSuspenseQuery>;
export type GetPipelineParameterChoicesQueryResult = Apollo.QueryResult<GetPipelineParameterChoicesQuery, GetPipelineParameterChoicesQueryVariables>;
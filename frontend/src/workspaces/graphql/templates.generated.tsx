import * as Types from '../../graphql/types';

import { gql } from '@apollo/client';
import * as Apollo from '@apollo/client';
const defaultOptions = {} as const;
export type GetPipelineVersionForTemplateQueryVariables = Types.Exact<{
  versionId: Types.Scalars['UUID']['input'];
}>;


export type GetPipelineVersionForTemplateQuery = { __typename?: 'Query', pipelineVersion?: { __typename?: 'PipelineVersion', id: string, zipfile: string } | null };


export const GetPipelineVersionForTemplateDocument = gql`
    query GetPipelineVersionForTemplate($versionId: UUID!) {
  pipelineVersion(id: $versionId) {
    id
    zipfile
  }
}
    `;

/**
 * __useGetPipelineVersionForTemplateQuery__
 *
 * To run a query within a React component, call `useGetPipelineVersionForTemplateQuery` and pass it any options that fit your needs.
 * When your component renders, `useGetPipelineVersionForTemplateQuery` returns an object from Apollo Client that contains loading, error, and data properties
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = useGetPipelineVersionForTemplateQuery({
 *   variables: {
 *      versionId: // value for 'versionId'
 *   },
 * });
 */
export function useGetPipelineVersionForTemplateQuery(baseOptions: Apollo.QueryHookOptions<GetPipelineVersionForTemplateQuery, GetPipelineVersionForTemplateQueryVariables> & ({ variables: GetPipelineVersionForTemplateQueryVariables; skip?: boolean; } | { skip: boolean; }) ) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useQuery<GetPipelineVersionForTemplateQuery, GetPipelineVersionForTemplateQueryVariables>(GetPipelineVersionForTemplateDocument, options);
      }
export function useGetPipelineVersionForTemplateLazyQuery(baseOptions?: Apollo.LazyQueryHookOptions<GetPipelineVersionForTemplateQuery, GetPipelineVersionForTemplateQueryVariables>) {
          const options = {...defaultOptions, ...baseOptions}
          return Apollo.useLazyQuery<GetPipelineVersionForTemplateQuery, GetPipelineVersionForTemplateQueryVariables>(GetPipelineVersionForTemplateDocument, options);
        }
export function useGetPipelineVersionForTemplateSuspenseQuery(baseOptions?: Apollo.SkipToken | Apollo.SuspenseQueryHookOptions<GetPipelineVersionForTemplateQuery, GetPipelineVersionForTemplateQueryVariables>) {
          const options = baseOptions === Apollo.skipToken ? baseOptions : {...defaultOptions, ...baseOptions}
          return Apollo.useSuspenseQuery<GetPipelineVersionForTemplateQuery, GetPipelineVersionForTemplateQueryVariables>(GetPipelineVersionForTemplateDocument, options);
        }
export type GetPipelineVersionForTemplateQueryHookResult = ReturnType<typeof useGetPipelineVersionForTemplateQuery>;
export type GetPipelineVersionForTemplateLazyQueryHookResult = ReturnType<typeof useGetPipelineVersionForTemplateLazyQuery>;
export type GetPipelineVersionForTemplateSuspenseQueryHookResult = ReturnType<typeof useGetPipelineVersionForTemplateSuspenseQuery>;
export type GetPipelineVersionForTemplateQueryResult = Apollo.QueryResult<GetPipelineVersionForTemplateQuery, GetPipelineVersionForTemplateQueryVariables>;
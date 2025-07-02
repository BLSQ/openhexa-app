import * as Types from '../../../graphql/types';

import { gql } from '@apollo/client';
import * as Apollo from '@apollo/client';
const defaultOptions = {} as const;
export type GetPipelineVersionFilesQueryVariables = Types.Exact<{
  versionId: Types.Scalars['UUID']['input'];
}>;


export type GetPipelineVersionFilesQuery = { __typename?: 'Query', pipelineVersion?: { __typename?: 'PipelineVersion', id: string, versionName: string, files: Array<{ __typename?: 'PipelineVersionFile', name: string, path: string, type: Types.FileType, content?: string | null }> } | null };


export const GetPipelineVersionFilesDocument = gql`
    query GetPipelineVersionFiles($versionId: UUID!) {
  pipelineVersion(id: $versionId) {
    id
    versionName
    files {
      name
      path
      type
      content
    }
  }
}
    `;

/**
 * __useGetPipelineVersionFilesQuery__
 *
 * To run a query within a React component, call `useGetPipelineVersionFilesQuery` and pass it any options that fit your needs.
 * When your component renders, `useGetPipelineVersionFilesQuery` returns an object from Apollo Client that contains loading, error, and data properties
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = useGetPipelineVersionFilesQuery({
 *   variables: {
 *      versionId: // value for 'versionId'
 *   },
 * });
 */
export function useGetPipelineVersionFilesQuery(baseOptions: Apollo.QueryHookOptions<GetPipelineVersionFilesQuery, GetPipelineVersionFilesQueryVariables> & ({ variables: GetPipelineVersionFilesQueryVariables; skip?: boolean; } | { skip: boolean; }) ) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useQuery<GetPipelineVersionFilesQuery, GetPipelineVersionFilesQueryVariables>(GetPipelineVersionFilesDocument, options);
      }
export function useGetPipelineVersionFilesLazyQuery(baseOptions?: Apollo.LazyQueryHookOptions<GetPipelineVersionFilesQuery, GetPipelineVersionFilesQueryVariables>) {
          const options = {...defaultOptions, ...baseOptions}
          return Apollo.useLazyQuery<GetPipelineVersionFilesQuery, GetPipelineVersionFilesQueryVariables>(GetPipelineVersionFilesDocument, options);
        }
export function useGetPipelineVersionFilesSuspenseQuery(baseOptions?: Apollo.SkipToken | Apollo.SuspenseQueryHookOptions<GetPipelineVersionFilesQuery, GetPipelineVersionFilesQueryVariables>) {
          const options = baseOptions === Apollo.skipToken ? baseOptions : {...defaultOptions, ...baseOptions}
          return Apollo.useSuspenseQuery<GetPipelineVersionFilesQuery, GetPipelineVersionFilesQueryVariables>(GetPipelineVersionFilesDocument, options);
        }
export type GetPipelineVersionFilesQueryHookResult = ReturnType<typeof useGetPipelineVersionFilesQuery>;
export type GetPipelineVersionFilesLazyQueryHookResult = ReturnType<typeof useGetPipelineVersionFilesLazyQuery>;
export type GetPipelineVersionFilesSuspenseQueryHookResult = ReturnType<typeof useGetPipelineVersionFilesSuspenseQuery>;
export type GetPipelineVersionFilesQueryResult = Apollo.QueryResult<GetPipelineVersionFilesQuery, GetPipelineVersionFilesQueryVariables>;
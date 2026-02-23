import * as Types from '../../graphql/types';

import { gql } from '@apollo/client';
import * as Apollo from '@apollo/client';
const defaultOptions = {} as const;
export type GetTemplateVersionForDownloadQueryVariables = Types.Exact<{
  versionId: Types.Scalars['UUID']['input'];
}>;


export type GetTemplateVersionForDownloadQuery = { __typename?: 'Query', pipelineTemplateVersion?: { __typename?: 'PipelineTemplateVersion', id: string, versionNumber: number, template: { __typename?: 'PipelineTemplate', code: string }, sourcePipelineVersion: { __typename?: 'PipelineVersion', zipfile?: string | null } } | null };


export const GetTemplateVersionForDownloadDocument = gql`
    query GetTemplateVersionForDownload($versionId: UUID!) {
  pipelineTemplateVersion(id: $versionId) {
    id
    versionNumber
    template {
      code
    }
    sourcePipelineVersion {
      zipfile
    }
  }
}
    `;

/**
 * __useGetTemplateVersionForDownloadQuery__
 *
 * To run a query within a React component, call `useGetTemplateVersionForDownloadQuery` and pass it any options that fit your needs.
 * When your component renders, `useGetTemplateVersionForDownloadQuery` returns an object from Apollo Client that contains loading, error, and data properties
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = useGetTemplateVersionForDownloadQuery({
 *   variables: {
 *      versionId: // value for 'versionId'
 *   },
 * });
 */
export function useGetTemplateVersionForDownloadQuery(baseOptions: Apollo.QueryHookOptions<GetTemplateVersionForDownloadQuery, GetTemplateVersionForDownloadQueryVariables> & ({ variables: GetTemplateVersionForDownloadQueryVariables; skip?: boolean; } | { skip: boolean; }) ) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useQuery<GetTemplateVersionForDownloadQuery, GetTemplateVersionForDownloadQueryVariables>(GetTemplateVersionForDownloadDocument, options);
      }
export function useGetTemplateVersionForDownloadLazyQuery(baseOptions?: Apollo.LazyQueryHookOptions<GetTemplateVersionForDownloadQuery, GetTemplateVersionForDownloadQueryVariables>) {
          const options = {...defaultOptions, ...baseOptions}
          return Apollo.useLazyQuery<GetTemplateVersionForDownloadQuery, GetTemplateVersionForDownloadQueryVariables>(GetTemplateVersionForDownloadDocument, options);
        }
export function useGetTemplateVersionForDownloadSuspenseQuery(baseOptions?: Apollo.SkipToken | Apollo.SuspenseQueryHookOptions<GetTemplateVersionForDownloadQuery, GetTemplateVersionForDownloadQueryVariables>) {
          const options = baseOptions === Apollo.skipToken ? baseOptions : {...defaultOptions, ...baseOptions}
          return Apollo.useSuspenseQuery<GetTemplateVersionForDownloadQuery, GetTemplateVersionForDownloadQueryVariables>(GetTemplateVersionForDownloadDocument, options);
        }
export type GetTemplateVersionForDownloadQueryHookResult = ReturnType<typeof useGetTemplateVersionForDownloadQuery>;
export type GetTemplateVersionForDownloadLazyQueryHookResult = ReturnType<typeof useGetTemplateVersionForDownloadLazyQuery>;
export type GetTemplateVersionForDownloadSuspenseQueryHookResult = ReturnType<typeof useGetTemplateVersionForDownloadSuspenseQuery>;
export type GetTemplateVersionForDownloadQueryResult = Apollo.QueryResult<GetTemplateVersionForDownloadQuery, GetTemplateVersionForDownloadQueryVariables>;
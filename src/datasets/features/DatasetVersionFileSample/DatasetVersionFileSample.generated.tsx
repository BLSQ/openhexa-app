import * as Types from '../../../graphql/types';

import { gql } from '@apollo/client';
import * as Apollo from '@apollo/client';
const defaultOptions = {} as const;
export type GetDatasetVersionFileSampleQueryVariables = Types.Exact<{
  id: Types.Scalars['ID']['input'];
}>;


export type GetDatasetVersionFileSampleQuery = { __typename?: 'Query', datasetVersionFile?: { __typename?: 'DatasetVersionFile', id: string, properties?: any | null, fileSample?: { __typename?: 'DatasetFileSample', sample?: any | null, status: Types.FileSampleStatus, statusReason?: string | null } | null } | null };

export type DatasetVersionFileSample_FileFragment = { __typename?: 'DatasetVersionFile', id: string, filename: string, contentType: string, size: any, downloadUrl?: string | null };

export type DatasetVersionFileSample_VersionFragment = { __typename?: 'DatasetVersion', name: string, dataset: { __typename?: 'Dataset', slug: string, workspace?: { __typename?: 'Workspace', slug: string } | null } };

export const DatasetVersionFileSample_FileFragmentDoc = gql`
    fragment DatasetVersionFileSample_file on DatasetVersionFile {
  id
  filename
  contentType
  size
  downloadUrl(attachment: false)
}
    `;
export const DatasetVersionFileSample_VersionFragmentDoc = gql`
    fragment DatasetVersionFileSample_version on DatasetVersion {
  name
  dataset {
    slug
    workspace {
      slug
    }
  }
}
    `;
export const GetDatasetVersionFileSampleDocument = gql`
    query GetDatasetVersionFileSample($id: ID!) {
  datasetVersionFile(id: $id) {
    id
    properties
    fileSample {
      sample
      status
      statusReason
    }
  }
}
    `;

/**
 * __useGetDatasetVersionFileSampleQuery__
 *
 * To run a query within a React component, call `useGetDatasetVersionFileSampleQuery` and pass it any options that fit your needs.
 * When your component renders, `useGetDatasetVersionFileSampleQuery` returns an object from Apollo Client that contains loading, error, and data properties
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = useGetDatasetVersionFileSampleQuery({
 *   variables: {
 *      id: // value for 'id'
 *   },
 * });
 */
export function useGetDatasetVersionFileSampleQuery(baseOptions: Apollo.QueryHookOptions<GetDatasetVersionFileSampleQuery, GetDatasetVersionFileSampleQueryVariables> & ({ variables: GetDatasetVersionFileSampleQueryVariables; skip?: boolean; } | { skip: boolean; }) ) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useQuery<GetDatasetVersionFileSampleQuery, GetDatasetVersionFileSampleQueryVariables>(GetDatasetVersionFileSampleDocument, options);
      }
export function useGetDatasetVersionFileSampleLazyQuery(baseOptions?: Apollo.LazyQueryHookOptions<GetDatasetVersionFileSampleQuery, GetDatasetVersionFileSampleQueryVariables>) {
          const options = {...defaultOptions, ...baseOptions}
          return Apollo.useLazyQuery<GetDatasetVersionFileSampleQuery, GetDatasetVersionFileSampleQueryVariables>(GetDatasetVersionFileSampleDocument, options);
        }
export function useGetDatasetVersionFileSampleSuspenseQuery(baseOptions?: Apollo.SkipToken | Apollo.SuspenseQueryHookOptions<GetDatasetVersionFileSampleQuery, GetDatasetVersionFileSampleQueryVariables>) {
          const options = baseOptions === Apollo.skipToken ? baseOptions : {...defaultOptions, ...baseOptions}
          return Apollo.useSuspenseQuery<GetDatasetVersionFileSampleQuery, GetDatasetVersionFileSampleQueryVariables>(GetDatasetVersionFileSampleDocument, options);
        }
export type GetDatasetVersionFileSampleQueryHookResult = ReturnType<typeof useGetDatasetVersionFileSampleQuery>;
export type GetDatasetVersionFileSampleLazyQueryHookResult = ReturnType<typeof useGetDatasetVersionFileSampleLazyQuery>;
export type GetDatasetVersionFileSampleSuspenseQueryHookResult = ReturnType<typeof useGetDatasetVersionFileSampleSuspenseQuery>;
export type GetDatasetVersionFileSampleQueryResult = Apollo.QueryResult<GetDatasetVersionFileSampleQuery, GetDatasetVersionFileSampleQueryVariables>;
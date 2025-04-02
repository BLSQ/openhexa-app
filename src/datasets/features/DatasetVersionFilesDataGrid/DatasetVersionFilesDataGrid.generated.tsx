import * as Types from '../../../graphql/types';

import { gql } from '@apollo/client';
import { DownloadVersionFile_FileFragmentDoc } from '../DownloadVersionFile/DownloadVersionFile.generated';
import * as Apollo from '@apollo/client';
const defaultOptions = {} as const;
export type DatasetVersionFilesDataGridQueryVariables = Types.Exact<{
  versionId: Types.Scalars['ID']['input'];
  page?: Types.InputMaybe<Types.Scalars['Int']['input']>;
  perPage: Types.Scalars['Int']['input'];
}>;


export type DatasetVersionFilesDataGridQuery = { __typename?: 'Query', datasetVersion?: { __typename?: 'DatasetVersion', id: string, files: { __typename?: 'DatasetVersionFilePage', totalPages: number, totalItems: number, pageNumber: number, items: Array<{ __typename?: 'DatasetVersionFile', id: string, contentType: string, createdAt: any, uri: string, filename: string }> } } | null };

export type DatasetVersionFilesDataGrid_VersionFragment = { __typename?: 'DatasetVersion', id: string, name: string, permissions: { __typename?: 'DatasetVersionPermissions', download: boolean } };

export const DatasetVersionFilesDataGrid_VersionFragmentDoc = gql`
    fragment DatasetVersionFilesDataGrid_version on DatasetVersion {
  id
  name
  permissions {
    download
  }
}
    `;
export const DatasetVersionFilesDataGridDocument = gql`
    query DatasetVersionFilesDataGrid($versionId: ID!, $page: Int = 1, $perPage: Int!) {
  datasetVersion(id: $versionId) {
    id
    files(page: $page, perPage: $perPage) {
      items {
        ...DownloadVersionFile_file
        id
        contentType
        createdAt
        uri
        filename
      }
      totalPages
      totalItems
      pageNumber
    }
  }
}
    ${DownloadVersionFile_FileFragmentDoc}`;

/**
 * __useDatasetVersionFilesDataGridQuery__
 *
 * To run a query within a React component, call `useDatasetVersionFilesDataGridQuery` and pass it any options that fit your needs.
 * When your component renders, `useDatasetVersionFilesDataGridQuery` returns an object from Apollo Client that contains loading, error, and data properties
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = useDatasetVersionFilesDataGridQuery({
 *   variables: {
 *      versionId: // value for 'versionId'
 *      page: // value for 'page'
 *      perPage: // value for 'perPage'
 *   },
 * });
 */
export function useDatasetVersionFilesDataGridQuery(baseOptions: Apollo.QueryHookOptions<DatasetVersionFilesDataGridQuery, DatasetVersionFilesDataGridQueryVariables> & ({ variables: DatasetVersionFilesDataGridQueryVariables; skip?: boolean; } | { skip: boolean; }) ) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useQuery<DatasetVersionFilesDataGridQuery, DatasetVersionFilesDataGridQueryVariables>(DatasetVersionFilesDataGridDocument, options);
      }
export function useDatasetVersionFilesDataGridLazyQuery(baseOptions?: Apollo.LazyQueryHookOptions<DatasetVersionFilesDataGridQuery, DatasetVersionFilesDataGridQueryVariables>) {
          const options = {...defaultOptions, ...baseOptions}
          return Apollo.useLazyQuery<DatasetVersionFilesDataGridQuery, DatasetVersionFilesDataGridQueryVariables>(DatasetVersionFilesDataGridDocument, options);
        }
export function useDatasetVersionFilesDataGridSuspenseQuery(baseOptions?: Apollo.SkipToken | Apollo.SuspenseQueryHookOptions<DatasetVersionFilesDataGridQuery, DatasetVersionFilesDataGridQueryVariables>) {
          const options = baseOptions === Apollo.skipToken ? baseOptions : {...defaultOptions, ...baseOptions}
          return Apollo.useSuspenseQuery<DatasetVersionFilesDataGridQuery, DatasetVersionFilesDataGridQueryVariables>(DatasetVersionFilesDataGridDocument, options);
        }
export type DatasetVersionFilesDataGridQueryHookResult = ReturnType<typeof useDatasetVersionFilesDataGridQuery>;
export type DatasetVersionFilesDataGridLazyQueryHookResult = ReturnType<typeof useDatasetVersionFilesDataGridLazyQuery>;
export type DatasetVersionFilesDataGridSuspenseQueryHookResult = ReturnType<typeof useDatasetVersionFilesDataGridSuspenseQuery>;
export type DatasetVersionFilesDataGridQueryResult = Apollo.QueryResult<DatasetVersionFilesDataGridQuery, DatasetVersionFilesDataGridQueryVariables>;
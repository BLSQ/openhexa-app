import * as Types from '../../../graphql/types';

import { gql } from '@apollo/client';
import * as Apollo from '@apollo/client';
const defaultOptions = {} as const;
export type DatasetVersionFileColumnsMetadataQueryVariables = Types.Exact<{
  id: Types.Scalars['ID']['input'];
}>;


export type DatasetVersionFileColumnsMetadataQuery = { __typename?: 'Query', datasetVersionFile?: { __typename?: 'DatasetVersionFile', id: string, attributes: Array<{ __typename?: 'MetadataAttribute', id: string, key: string, value?: any | null, system: boolean }> } | null };

export type DatasetVersionFileColumns_FileFragment = { __typename?: 'DatasetVersionFile', id: string };

export const DatasetVersionFileColumns_FileFragmentDoc = gql`
    fragment DatasetVersionFileColumns_file on DatasetVersionFile {
  id
}
    `;
export const DatasetVersionFileColumnsMetadataDocument = gql`
    query DatasetVersionFileColumnsMetadata($id: ID!) {
  datasetVersionFile(id: $id) {
    id
    attributes {
      id
      key
      value
      system
    }
  }
}
    `;

/**
 * __useDatasetVersionFileColumnsMetadataQuery__
 *
 * To run a query within a React component, call `useDatasetVersionFileColumnsMetadataQuery` and pass it any options that fit your needs.
 * When your component renders, `useDatasetVersionFileColumnsMetadataQuery` returns an object from Apollo Client that contains loading, error, and data properties
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = useDatasetVersionFileColumnsMetadataQuery({
 *   variables: {
 *      id: // value for 'id'
 *   },
 * });
 */
export function useDatasetVersionFileColumnsMetadataQuery(baseOptions: Apollo.QueryHookOptions<DatasetVersionFileColumnsMetadataQuery, DatasetVersionFileColumnsMetadataQueryVariables> & ({ variables: DatasetVersionFileColumnsMetadataQueryVariables; skip?: boolean; } | { skip: boolean; }) ) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useQuery<DatasetVersionFileColumnsMetadataQuery, DatasetVersionFileColumnsMetadataQueryVariables>(DatasetVersionFileColumnsMetadataDocument, options);
      }
export function useDatasetVersionFileColumnsMetadataLazyQuery(baseOptions?: Apollo.LazyQueryHookOptions<DatasetVersionFileColumnsMetadataQuery, DatasetVersionFileColumnsMetadataQueryVariables>) {
          const options = {...defaultOptions, ...baseOptions}
          return Apollo.useLazyQuery<DatasetVersionFileColumnsMetadataQuery, DatasetVersionFileColumnsMetadataQueryVariables>(DatasetVersionFileColumnsMetadataDocument, options);
        }
export function useDatasetVersionFileColumnsMetadataSuspenseQuery(baseOptions?: Apollo.SkipToken | Apollo.SuspenseQueryHookOptions<DatasetVersionFileColumnsMetadataQuery, DatasetVersionFileColumnsMetadataQueryVariables>) {
          const options = baseOptions === Apollo.skipToken ? baseOptions : {...defaultOptions, ...baseOptions}
          return Apollo.useSuspenseQuery<DatasetVersionFileColumnsMetadataQuery, DatasetVersionFileColumnsMetadataQueryVariables>(DatasetVersionFileColumnsMetadataDocument, options);
        }
export type DatasetVersionFileColumnsMetadataQueryHookResult = ReturnType<typeof useDatasetVersionFileColumnsMetadataQuery>;
export type DatasetVersionFileColumnsMetadataLazyQueryHookResult = ReturnType<typeof useDatasetVersionFileColumnsMetadataLazyQuery>;
export type DatasetVersionFileColumnsMetadataSuspenseQueryHookResult = ReturnType<typeof useDatasetVersionFileColumnsMetadataSuspenseQuery>;
export type DatasetVersionFileColumnsMetadataQueryResult = Apollo.QueryResult<DatasetVersionFileColumnsMetadataQuery, DatasetVersionFileColumnsMetadataQueryVariables>;
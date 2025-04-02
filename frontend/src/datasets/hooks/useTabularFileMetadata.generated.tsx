import * as Types from '../../graphql/types';

import { gql } from '@apollo/client';
import * as Apollo from '@apollo/client';
const defaultOptions = {} as const;
export type TabularFileMetadataQueryVariables = Types.Exact<{
  fileId: Types.Scalars['ID']['input'];
}>;


export type TabularFileMetadataQuery = { __typename?: 'Query', datasetVersionFile?: { __typename?: 'DatasetVersionFile', properties?: any | null, id: string, targetId: any, attributes: Array<{ __typename?: 'MetadataAttribute', id: string, key: string, value?: any | null, label?: string | null, system: boolean, createdAt: any, updatedAt: any, createdBy?: { __typename?: 'User', displayName: string } | null, updatedBy?: { __typename?: 'User', displayName: string } | null }> } | null };


export const TabularFileMetadataDocument = gql`
    query TabularFileMetadata($fileId: ID!) {
  datasetVersionFile(id: $fileId) {
    attributes {
      id
      key
      value
      label
      system
      createdAt
      updatedAt
      createdBy {
        displayName
      }
      updatedBy {
        displayName
      }
    }
    properties
    id
    targetId
  }
}
    `;

/**
 * __useTabularFileMetadataQuery__
 *
 * To run a query within a React component, call `useTabularFileMetadataQuery` and pass it any options that fit your needs.
 * When your component renders, `useTabularFileMetadataQuery` returns an object from Apollo Client that contains loading, error, and data properties
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = useTabularFileMetadataQuery({
 *   variables: {
 *      fileId: // value for 'fileId'
 *   },
 * });
 */
export function useTabularFileMetadataQuery(baseOptions: Apollo.QueryHookOptions<TabularFileMetadataQuery, TabularFileMetadataQueryVariables> & ({ variables: TabularFileMetadataQueryVariables; skip?: boolean; } | { skip: boolean; }) ) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useQuery<TabularFileMetadataQuery, TabularFileMetadataQueryVariables>(TabularFileMetadataDocument, options);
      }
export function useTabularFileMetadataLazyQuery(baseOptions?: Apollo.LazyQueryHookOptions<TabularFileMetadataQuery, TabularFileMetadataQueryVariables>) {
          const options = {...defaultOptions, ...baseOptions}
          return Apollo.useLazyQuery<TabularFileMetadataQuery, TabularFileMetadataQueryVariables>(TabularFileMetadataDocument, options);
        }
export function useTabularFileMetadataSuspenseQuery(baseOptions?: Apollo.SkipToken | Apollo.SuspenseQueryHookOptions<TabularFileMetadataQuery, TabularFileMetadataQueryVariables>) {
          const options = baseOptions === Apollo.skipToken ? baseOptions : {...defaultOptions, ...baseOptions}
          return Apollo.useSuspenseQuery<TabularFileMetadataQuery, TabularFileMetadataQueryVariables>(TabularFileMetadataDocument, options);
        }
export type TabularFileMetadataQueryHookResult = ReturnType<typeof useTabularFileMetadataQuery>;
export type TabularFileMetadataLazyQueryHookResult = ReturnType<typeof useTabularFileMetadataLazyQuery>;
export type TabularFileMetadataSuspenseQueryHookResult = ReturnType<typeof useTabularFileMetadataSuspenseQuery>;
export type TabularFileMetadataQueryResult = Apollo.QueryResult<TabularFileMetadataQuery, TabularFileMetadataQueryVariables>;
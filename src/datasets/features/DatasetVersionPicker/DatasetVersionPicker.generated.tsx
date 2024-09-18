import * as Types from '../../../graphql/types';

import { gql } from '@apollo/client';
import * as Apollo from '@apollo/client';
const defaultOptions = {} as const;
export type DatasetVersionPickerQueryVariables = Types.Exact<{
  datasetId: Types.Scalars['ID']['input'];
  perPage: Types.Scalars['Int']['input'];
}>;


export type DatasetVersionPickerQuery = { __typename?: 'Query', dataset?: { __typename?: 'Dataset', versions: { __typename?: 'DatasetVersionPage', totalItems: number, items: Array<{ __typename?: 'DatasetVersion', id: string, name: string, createdAt: any }> } } | null };

export type DatasetVersionPicker_VersionFragment = { __typename?: 'DatasetVersion', id: string, name: string, createdAt: any };

export type DatasetVersionPicker_DatasetFragment = { __typename?: 'Dataset', id: string };

export const DatasetVersionPicker_VersionFragmentDoc = gql`
    fragment DatasetVersionPicker_version on DatasetVersion {
  id
  name
  createdAt
}
    `;
export const DatasetVersionPicker_DatasetFragmentDoc = gql`
    fragment DatasetVersionPicker_dataset on Dataset {
  id
}
    `;
export const DatasetVersionPickerDocument = gql`
    query DatasetVersionPicker($datasetId: ID!, $perPage: Int!) {
  dataset(id: $datasetId) {
    versions(perPage: $perPage) {
      totalItems
      items {
        ...DatasetVersionPicker_version
      }
    }
  }
}
    ${DatasetVersionPicker_VersionFragmentDoc}`;

/**
 * __useDatasetVersionPickerQuery__
 *
 * To run a query within a React component, call `useDatasetVersionPickerQuery` and pass it any options that fit your needs.
 * When your component renders, `useDatasetVersionPickerQuery` returns an object from Apollo Client that contains loading, error, and data properties
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = useDatasetVersionPickerQuery({
 *   variables: {
 *      datasetId: // value for 'datasetId'
 *      perPage: // value for 'perPage'
 *   },
 * });
 */
export function useDatasetVersionPickerQuery(baseOptions: Apollo.QueryHookOptions<DatasetVersionPickerQuery, DatasetVersionPickerQueryVariables> & ({ variables: DatasetVersionPickerQueryVariables; skip?: boolean; } | { skip: boolean; }) ) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useQuery<DatasetVersionPickerQuery, DatasetVersionPickerQueryVariables>(DatasetVersionPickerDocument, options);
      }
export function useDatasetVersionPickerLazyQuery(baseOptions?: Apollo.LazyQueryHookOptions<DatasetVersionPickerQuery, DatasetVersionPickerQueryVariables>) {
          const options = {...defaultOptions, ...baseOptions}
          return Apollo.useLazyQuery<DatasetVersionPickerQuery, DatasetVersionPickerQueryVariables>(DatasetVersionPickerDocument, options);
        }
export function useDatasetVersionPickerSuspenseQuery(baseOptions?: Apollo.SkipToken | Apollo.SuspenseQueryHookOptions<DatasetVersionPickerQuery, DatasetVersionPickerQueryVariables>) {
          const options = baseOptions === Apollo.skipToken ? baseOptions : {...defaultOptions, ...baseOptions}
          return Apollo.useSuspenseQuery<DatasetVersionPickerQuery, DatasetVersionPickerQueryVariables>(DatasetVersionPickerDocument, options);
        }
export type DatasetVersionPickerQueryHookResult = ReturnType<typeof useDatasetVersionPickerQuery>;
export type DatasetVersionPickerLazyQueryHookResult = ReturnType<typeof useDatasetVersionPickerLazyQuery>;
export type DatasetVersionPickerSuspenseQueryHookResult = ReturnType<typeof useDatasetVersionPickerSuspenseQuery>;
export type DatasetVersionPickerQueryResult = Apollo.QueryResult<DatasetVersionPickerQuery, DatasetVersionPickerQueryVariables>;
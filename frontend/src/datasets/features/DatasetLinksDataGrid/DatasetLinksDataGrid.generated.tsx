import * as Types from '../../../graphql/types';

import { gql } from '@apollo/client';
import { DeleteDatasetLinkTrigger_DatasetLinkFragmentDoc } from '../DeleteDatasetLinkTrigger/DeleteDatasetLinkTrigger.generated';
import * as Apollo from '@apollo/client';
const defaultOptions = {} as const;
export type DatasetLinksDataGridQueryVariables = Types.Exact<{
  datasetId: Types.Scalars['ID']['input'];
  page?: Types.InputMaybe<Types.Scalars['Int']['input']>;
}>;


export type DatasetLinksDataGridQuery = { __typename?: 'Query', dataset?: { __typename?: 'Dataset', links: { __typename?: 'DatasetLinkPage', totalItems: number, items: Array<{ __typename?: 'DatasetLink', createdAt: any, id: string, permissions: { __typename?: 'DatasetLinkPermissions', delete: boolean }, workspace: { __typename?: 'Workspace', slug: string, name: string }, createdBy?: { __typename?: 'User', displayName: string } | null, dataset: { __typename?: 'Dataset', name: string, id: string } }> } } | null };

export type DatasetLinksDataGrid_DatasetFragment = { __typename?: 'Dataset', id: string, name: string };

export const DatasetLinksDataGrid_DatasetFragmentDoc = gql`
    fragment DatasetLinksDataGrid_dataset on Dataset {
  id
  name
}
    `;
export const DatasetLinksDataGridDocument = gql`
    query DatasetLinksDataGrid($datasetId: ID!, $page: Int) {
  dataset(id: $datasetId) {
    links(page: $page, perPage: 6) {
      totalItems
      items {
        ...DeleteDatasetLinkTrigger_datasetLink
        permissions {
          delete
        }
        workspace {
          slug
          name
        }
        createdBy {
          displayName
        }
        createdAt
      }
    }
  }
}
    ${DeleteDatasetLinkTrigger_DatasetLinkFragmentDoc}`;

/**
 * __useDatasetLinksDataGridQuery__
 *
 * To run a query within a React component, call `useDatasetLinksDataGridQuery` and pass it any options that fit your needs.
 * When your component renders, `useDatasetLinksDataGridQuery` returns an object from Apollo Client that contains loading, error, and data properties
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = useDatasetLinksDataGridQuery({
 *   variables: {
 *      datasetId: // value for 'datasetId'
 *      page: // value for 'page'
 *   },
 * });
 */
export function useDatasetLinksDataGridQuery(baseOptions: Apollo.QueryHookOptions<DatasetLinksDataGridQuery, DatasetLinksDataGridQueryVariables> & ({ variables: DatasetLinksDataGridQueryVariables; skip?: boolean; } | { skip: boolean; }) ) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useQuery<DatasetLinksDataGridQuery, DatasetLinksDataGridQueryVariables>(DatasetLinksDataGridDocument, options);
      }
export function useDatasetLinksDataGridLazyQuery(baseOptions?: Apollo.LazyQueryHookOptions<DatasetLinksDataGridQuery, DatasetLinksDataGridQueryVariables>) {
          const options = {...defaultOptions, ...baseOptions}
          return Apollo.useLazyQuery<DatasetLinksDataGridQuery, DatasetLinksDataGridQueryVariables>(DatasetLinksDataGridDocument, options);
        }
export function useDatasetLinksDataGridSuspenseQuery(baseOptions?: Apollo.SkipToken | Apollo.SuspenseQueryHookOptions<DatasetLinksDataGridQuery, DatasetLinksDataGridQueryVariables>) {
          const options = baseOptions === Apollo.skipToken ? baseOptions : {...defaultOptions, ...baseOptions}
          return Apollo.useSuspenseQuery<DatasetLinksDataGridQuery, DatasetLinksDataGridQueryVariables>(DatasetLinksDataGridDocument, options);
        }
export type DatasetLinksDataGridQueryHookResult = ReturnType<typeof useDatasetLinksDataGridQuery>;
export type DatasetLinksDataGridLazyQueryHookResult = ReturnType<typeof useDatasetLinksDataGridLazyQuery>;
export type DatasetLinksDataGridSuspenseQueryHookResult = ReturnType<typeof useDatasetLinksDataGridSuspenseQuery>;
export type DatasetLinksDataGridQueryResult = Apollo.QueryResult<DatasetLinksDataGridQuery, DatasetLinksDataGridQueryVariables>;
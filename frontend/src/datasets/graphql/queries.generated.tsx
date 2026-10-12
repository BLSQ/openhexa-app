import * as Types from '../../graphql/types';

import { gql } from '@apollo/client';
import { DatasetPicker_WorkspaceFragmentDoc } from '../features/DatasetPicker/DatasetPicker.generated';
import { DatasetVersionPicker_VersionFragmentDoc, DatasetVersionPicker_DatasetFragmentDoc } from '../features/DatasetVersionPicker/DatasetVersionPicker.generated';
import { DatasetExplorer_VersionFragmentDoc } from '../features/DatasetExplorer/DatasetExplorer.generated';
import * as Apollo from '@apollo/client';
const defaultOptions = {} as const;
export type DatasetPickerQueryVariables = Types.Exact<{
  slug: Types.Scalars['String']['input'];
}>;


export type DatasetPickerQuery = { __typename?: 'Query', workspace?: { __typename?: 'Workspace', slug: string, datasets: { __typename?: 'DatasetLinkPage', items: Array<{ __typename?: 'DatasetLink', id: string, dataset: { __typename?: 'Dataset', slug: string, name: string } }> } } | null };

export type DatasetVersionPickerQueryVariables = Types.Exact<{
  datasetId: Types.Scalars['ID']['input'];
  perPage: Types.Scalars['Int']['input'];
}>;


export type DatasetVersionPickerQuery = { __typename?: 'Query', dataset?: { __typename?: 'Dataset', versions: { __typename?: 'DatasetVersionPage', totalItems: number, items: Array<{ __typename?: 'DatasetVersion', id: string, name: string, createdAt: any }> } } | null };

export type PublicDatasetPage_VersionFragment = { __typename?: 'DatasetVersion', id: string, name: string, changelog?: string | null, createdAt: any, files: { __typename?: 'DatasetVersionFilePage', totalPages: number, pageNumber: number, totalItems: number, items: Array<{ __typename?: 'DatasetVersionFile', id: string, filename: string, createdAt: any, contentType: string, size: any, uri: string, downloadUrl?: string | null, targetId: any, properties?: any | null, createdBy?: { __typename?: 'User', displayName: string } | null, attributes: Array<{ __typename: 'MetadataAttribute', id: string, key: string, value?: any | null, label?: string | null, system: boolean }> }> }, dataset: { __typename?: 'Dataset', slug: string, workspace?: { __typename?: 'Workspace', slug: string } | null, permissions: { __typename?: 'DatasetPermissions', update: boolean } } };

export type PublicDatasetPageQueryVariables = Types.Exact<{
  datasetId: Types.Scalars['ID']['input'];
  versionId: Types.Scalars['ID']['input'];
  isSpecificVersion: Types.Scalars['Boolean']['input'];
  page?: Types.InputMaybe<Types.Scalars['Int']['input']>;
  perPage?: Types.InputMaybe<Types.Scalars['Int']['input']>;
}>;


export type PublicDatasetPageQuery = { __typename?: 'Query', dataset?: { __typename?: 'Dataset', id: string, name: string, slug: string, description?: string | null, visibility: Types.DatasetVisibility, createdAt: any, updatedAt: any, workspace?: { __typename?: 'Workspace', slug: string, name: string, organization: { __typename?: 'Organization', name: string } } | null, version?: { __typename?: 'DatasetVersion', id: string, name: string, changelog?: string | null, createdAt: any, files: { __typename?: 'DatasetVersionFilePage', totalPages: number, pageNumber: number, totalItems: number, items: Array<{ __typename?: 'DatasetVersionFile', id: string, filename: string, createdAt: any, contentType: string, size: any, uri: string, downloadUrl?: string | null, targetId: any, properties?: any | null, createdBy?: { __typename?: 'User', displayName: string } | null, attributes: Array<{ __typename: 'MetadataAttribute', id: string, key: string, value?: any | null, label?: string | null, system: boolean }> }> }, dataset: { __typename?: 'Dataset', slug: string, workspace?: { __typename?: 'Workspace', slug: string } | null, permissions: { __typename?: 'DatasetPermissions', update: boolean } } } | null, latestVersion?: { __typename?: 'DatasetVersion', id: string, name: string, changelog?: string | null, createdAt: any, files: { __typename?: 'DatasetVersionFilePage', totalPages: number, pageNumber: number, totalItems: number, items: Array<{ __typename?: 'DatasetVersionFile', id: string, filename: string, createdAt: any, contentType: string, size: any, uri: string, downloadUrl?: string | null, targetId: any, properties?: any | null, createdBy?: { __typename?: 'User', displayName: string } | null, attributes: Array<{ __typename: 'MetadataAttribute', id: string, key: string, value?: any | null, label?: string | null, system: boolean }> }> }, dataset: { __typename?: 'Dataset', slug: string, workspace?: { __typename?: 'Workspace', slug: string } | null, permissions: { __typename?: 'DatasetPermissions', update: boolean } } } | null } | null };

export const PublicDatasetPage_VersionFragmentDoc = gql`
    fragment PublicDatasetPage_version on DatasetVersion {
  id
  name
  changelog
  createdAt
  ...DatasetVersionPicker_version
  ...DatasetExplorer_version
}
    ${DatasetVersionPicker_VersionFragmentDoc}
${DatasetExplorer_VersionFragmentDoc}`;
export const DatasetPickerDocument = gql`
    query DatasetPicker($slug: String!) {
  workspace(slug: $slug) {
    slug
    ...DatasetPicker_workspace
  }
}
    ${DatasetPicker_WorkspaceFragmentDoc}`;

/**
 * __useDatasetPickerQuery__
 *
 * To run a query within a React component, call `useDatasetPickerQuery` and pass it any options that fit your needs.
 * When your component renders, `useDatasetPickerQuery` returns an object from Apollo Client that contains loading, error, and data properties
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = useDatasetPickerQuery({
 *   variables: {
 *      slug: // value for 'slug'
 *   },
 * });
 */
export function useDatasetPickerQuery(baseOptions: Apollo.QueryHookOptions<DatasetPickerQuery, DatasetPickerQueryVariables> & ({ variables: DatasetPickerQueryVariables; skip?: boolean; } | { skip: boolean; }) ) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useQuery<DatasetPickerQuery, DatasetPickerQueryVariables>(DatasetPickerDocument, options);
      }
export function useDatasetPickerLazyQuery(baseOptions?: Apollo.LazyQueryHookOptions<DatasetPickerQuery, DatasetPickerQueryVariables>) {
          const options = {...defaultOptions, ...baseOptions}
          return Apollo.useLazyQuery<DatasetPickerQuery, DatasetPickerQueryVariables>(DatasetPickerDocument, options);
        }
export function useDatasetPickerSuspenseQuery(baseOptions?: Apollo.SkipToken | Apollo.SuspenseQueryHookOptions<DatasetPickerQuery, DatasetPickerQueryVariables>) {
          const options = baseOptions === Apollo.skipToken ? baseOptions : {...defaultOptions, ...baseOptions}
          return Apollo.useSuspenseQuery<DatasetPickerQuery, DatasetPickerQueryVariables>(DatasetPickerDocument, options);
        }
export type DatasetPickerQueryHookResult = ReturnType<typeof useDatasetPickerQuery>;
export type DatasetPickerLazyQueryHookResult = ReturnType<typeof useDatasetPickerLazyQuery>;
export type DatasetPickerSuspenseQueryHookResult = ReturnType<typeof useDatasetPickerSuspenseQuery>;
export type DatasetPickerQueryResult = Apollo.QueryResult<DatasetPickerQuery, DatasetPickerQueryVariables>;
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
export const PublicDatasetPageDocument = gql`
    query PublicDatasetPage($datasetId: ID!, $versionId: ID!, $isSpecificVersion: Boolean!, $page: Int = 1, $perPage: Int = 20) {
  dataset(id: $datasetId) {
    id
    name
    slug
    description
    visibility
    createdAt
    updatedAt
    workspace {
      slug
      name
      organization {
        name
      }
    }
    ...DatasetVersionPicker_dataset
    version(id: $versionId) @include(if: $isSpecificVersion) {
      ...PublicDatasetPage_version
    }
    latestVersion @skip(if: $isSpecificVersion) {
      ...PublicDatasetPage_version
    }
  }
}
    ${DatasetVersionPicker_DatasetFragmentDoc}
${PublicDatasetPage_VersionFragmentDoc}`;

/**
 * __usePublicDatasetPageQuery__
 *
 * To run a query within a React component, call `usePublicDatasetPageQuery` and pass it any options that fit your needs.
 * When your component renders, `usePublicDatasetPageQuery` returns an object from Apollo Client that contains loading, error, and data properties
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = usePublicDatasetPageQuery({
 *   variables: {
 *      datasetId: // value for 'datasetId'
 *      versionId: // value for 'versionId'
 *      isSpecificVersion: // value for 'isSpecificVersion'
 *      page: // value for 'page'
 *      perPage: // value for 'perPage'
 *   },
 * });
 */
export function usePublicDatasetPageQuery(baseOptions: Apollo.QueryHookOptions<PublicDatasetPageQuery, PublicDatasetPageQueryVariables> & ({ variables: PublicDatasetPageQueryVariables; skip?: boolean; } | { skip: boolean; }) ) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useQuery<PublicDatasetPageQuery, PublicDatasetPageQueryVariables>(PublicDatasetPageDocument, options);
      }
export function usePublicDatasetPageLazyQuery(baseOptions?: Apollo.LazyQueryHookOptions<PublicDatasetPageQuery, PublicDatasetPageQueryVariables>) {
          const options = {...defaultOptions, ...baseOptions}
          return Apollo.useLazyQuery<PublicDatasetPageQuery, PublicDatasetPageQueryVariables>(PublicDatasetPageDocument, options);
        }
export function usePublicDatasetPageSuspenseQuery(baseOptions?: Apollo.SkipToken | Apollo.SuspenseQueryHookOptions<PublicDatasetPageQuery, PublicDatasetPageQueryVariables>) {
          const options = baseOptions === Apollo.skipToken ? baseOptions : {...defaultOptions, ...baseOptions}
          return Apollo.useSuspenseQuery<PublicDatasetPageQuery, PublicDatasetPageQueryVariables>(PublicDatasetPageDocument, options);
        }
export type PublicDatasetPageQueryHookResult = ReturnType<typeof usePublicDatasetPageQuery>;
export type PublicDatasetPageLazyQueryHookResult = ReturnType<typeof usePublicDatasetPageLazyQuery>;
export type PublicDatasetPageSuspenseQueryHookResult = ReturnType<typeof usePublicDatasetPageSuspenseQuery>;
export type PublicDatasetPageQueryResult = Apollo.QueryResult<PublicDatasetPageQuery, PublicDatasetPageQueryVariables>;
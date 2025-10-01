import * as Types from '../../../graphql/types';

import { gql } from '@apollo/client';
import { DatasetsPageFragmentDoc } from './DatasetResultTable.generated';
import { PipelinesPageFragmentDoc } from './PipelineResultTable.generated';
import { PipelineTemplatesPageFragmentDoc } from './PipelineTemplateResultTable.generated';
import { DatabaseTablesPageFragmentDoc } from './DatabaseTableResultTable.generated';
import { FilesPageFragmentDoc } from './FileResultTable.generated';
import { WorkspaceDisplayFragmentFragmentDoc } from './WorkspaceDisplay.generated';
import * as Apollo from '@apollo/client';
const defaultOptions = {} as const;
export type SearchDatasetsQueryVariables = Types.Exact<{
  query: Types.Scalars['String']['input'];
  workspaceSlugs: Array<Types.InputMaybe<Types.Scalars['String']['input']>> | Types.InputMaybe<Types.Scalars['String']['input']>;
  page?: Types.InputMaybe<Types.Scalars['Int']['input']>;
  perPage?: Types.InputMaybe<Types.Scalars['Int']['input']>;
}>;


export type SearchDatasetsQuery = { __typename?: 'Query', datasets: { __typename: 'DatasetResultPage', totalItems: number, pageNumber: number, totalPages: number, items: Array<{ __typename?: 'DatasetResult', score: number, dataset: { __typename?: 'Dataset', id: string, slug: string, name: string, description?: string | null, updatedAt: any, workspace?: { __typename?: 'Workspace', slug: string, name: string, countries: Array<{ __typename?: 'Country', code: string }> } | null, createdBy?: { __typename?: 'User', id: string, displayName: string, avatar: { __typename?: 'Avatar', initials: string, color: string } } | null } }> } };

export type SearchPipelinesQueryVariables = Types.Exact<{
  query: Types.Scalars['String']['input'];
  workspaceSlugs: Array<Types.InputMaybe<Types.Scalars['String']['input']>> | Types.InputMaybe<Types.Scalars['String']['input']>;
  page?: Types.InputMaybe<Types.Scalars['Int']['input']>;
  perPage?: Types.InputMaybe<Types.Scalars['Int']['input']>;
}>;


export type SearchPipelinesQuery = { __typename?: 'Query', pipelines: { __typename: 'PipelineResultPage', totalItems: number, pageNumber: number, totalPages: number, items: Array<{ __typename?: 'PipelineResult', score: number, pipeline: { __typename?: 'Pipeline', id: string, code: string, name?: string | null, description?: string | null, updatedAt?: any | null, tags: Array<{ __typename?: 'Tag', id: string, name: string }>, workspace: { __typename?: 'Workspace', slug: string, name: string, countries: Array<{ __typename?: 'Country', code: string }> }, lastRuns: { __typename?: 'PipelineRunPage', items: Array<{ __typename?: 'PipelineRun', id: string, status: Types.PipelineRunStatus }> } } }> } };

export type SearchPipelineTemplatesQueryVariables = Types.Exact<{
  query: Types.Scalars['String']['input'];
  workspaceSlugs: Array<Types.InputMaybe<Types.Scalars['String']['input']>> | Types.InputMaybe<Types.Scalars['String']['input']>;
  page?: Types.InputMaybe<Types.Scalars['Int']['input']>;
  perPage?: Types.InputMaybe<Types.Scalars['Int']['input']>;
}>;


export type SearchPipelineTemplatesQuery = { __typename?: 'Query', pipelineTemplates: { __typename: 'PipelineTemplateResultPage', totalItems: number, pageNumber: number, totalPages: number, items: Array<{ __typename?: 'PipelineTemplateResult', score: number, pipelineTemplate: { __typename?: 'PipelineTemplate', id: string, code: string, name: string, description?: string | null, updatedAt: any, workspace?: { __typename?: 'Workspace', slug: string, name: string, countries: Array<{ __typename?: 'Country', code: string }> } | null, currentVersion?: { __typename?: 'PipelineTemplateVersion', id: string, versionNumber: number } | null } }> } };

export type SearchDatabaseTablesQueryVariables = Types.Exact<{
  query: Types.Scalars['String']['input'];
  workspaceSlugs: Array<Types.InputMaybe<Types.Scalars['String']['input']>> | Types.InputMaybe<Types.Scalars['String']['input']>;
  page?: Types.InputMaybe<Types.Scalars['Int']['input']>;
  perPage?: Types.InputMaybe<Types.Scalars['Int']['input']>;
}>;


export type SearchDatabaseTablesQuery = { __typename?: 'Query', databaseTables: { __typename: 'DatabaseTableResultPage', totalItems: number, pageNumber: number, totalPages: number, items: Array<{ __typename?: 'DatabaseTableResult', score: number, databaseTable: { __typename?: 'DatabaseTable', name: string, count?: number | null }, workspace: { __typename?: 'Workspace', slug: string, name: string, countries: Array<{ __typename?: 'Country', code: string }> } }> } };

export type SearchFilesQueryVariables = Types.Exact<{
  query: Types.Scalars['String']['input'];
  workspaceSlugs: Array<Types.InputMaybe<Types.Scalars['String']['input']>> | Types.InputMaybe<Types.Scalars['String']['input']>;
  page?: Types.InputMaybe<Types.Scalars['Int']['input']>;
  perPage?: Types.InputMaybe<Types.Scalars['Int']['input']>;
}>;


export type SearchFilesQuery = { __typename?: 'Query', files: { __typename: 'BucketObjectResultPage', totalItems: number, pageNumber: number, totalPages: number, items: Array<{ __typename?: 'BucketObjectResult', score: number, file: { __typename?: 'BucketObject', name: string, path: string, size?: any | null, updatedAt?: any | null, type: Types.BucketObjectType }, workspace: { __typename?: 'Workspace', slug: string, name: string, countries: Array<{ __typename?: 'Country', code: string }> } }> } };

export type GetWorkspacesQueryVariables = Types.Exact<{
  organizationId?: Types.InputMaybe<Types.Scalars['UUID']['input']>;
  page?: Types.InputMaybe<Types.Scalars['Int']['input']>;
  perPage?: Types.InputMaybe<Types.Scalars['Int']['input']>;
}>;


export type GetWorkspacesQuery = { __typename?: 'Query', workspaces: { __typename?: 'WorkspacePage', totalItems: number, items: Array<{ __typename?: 'Workspace', slug: string, name: string, countries: Array<{ __typename?: 'Country', code: string }> }> } };


export const SearchDatasetsDocument = gql`
    query SearchDatasets($query: String!, $workspaceSlugs: [String]!, $page: Int, $perPage: Int) {
  datasets: searchDatasets(
    query: $query
    workspaceSlugs: $workspaceSlugs
    page: $page
    perPage: $perPage
  ) {
    __typename
    ...DatasetsPage
  }
}
    ${DatasetsPageFragmentDoc}`;

/**
 * __useSearchDatasetsQuery__
 *
 * To run a query within a React component, call `useSearchDatasetsQuery` and pass it any options that fit your needs.
 * When your component renders, `useSearchDatasetsQuery` returns an object from Apollo Client that contains loading, error, and data properties
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = useSearchDatasetsQuery({
 *   variables: {
 *      query: // value for 'query'
 *      workspaceSlugs: // value for 'workspaceSlugs'
 *      page: // value for 'page'
 *      perPage: // value for 'perPage'
 *   },
 * });
 */
export function useSearchDatasetsQuery(baseOptions: Apollo.QueryHookOptions<SearchDatasetsQuery, SearchDatasetsQueryVariables> & ({ variables: SearchDatasetsQueryVariables; skip?: boolean; } | { skip: boolean; }) ) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useQuery<SearchDatasetsQuery, SearchDatasetsQueryVariables>(SearchDatasetsDocument, options);
      }
export function useSearchDatasetsLazyQuery(baseOptions?: Apollo.LazyQueryHookOptions<SearchDatasetsQuery, SearchDatasetsQueryVariables>) {
          const options = {...defaultOptions, ...baseOptions}
          return Apollo.useLazyQuery<SearchDatasetsQuery, SearchDatasetsQueryVariables>(SearchDatasetsDocument, options);
        }
export function useSearchDatasetsSuspenseQuery(baseOptions?: Apollo.SkipToken | Apollo.SuspenseQueryHookOptions<SearchDatasetsQuery, SearchDatasetsQueryVariables>) {
          const options = baseOptions === Apollo.skipToken ? baseOptions : {...defaultOptions, ...baseOptions}
          return Apollo.useSuspenseQuery<SearchDatasetsQuery, SearchDatasetsQueryVariables>(SearchDatasetsDocument, options);
        }
export type SearchDatasetsQueryHookResult = ReturnType<typeof useSearchDatasetsQuery>;
export type SearchDatasetsLazyQueryHookResult = ReturnType<typeof useSearchDatasetsLazyQuery>;
export type SearchDatasetsSuspenseQueryHookResult = ReturnType<typeof useSearchDatasetsSuspenseQuery>;
export type SearchDatasetsQueryResult = Apollo.QueryResult<SearchDatasetsQuery, SearchDatasetsQueryVariables>;
export const SearchPipelinesDocument = gql`
    query SearchPipelines($query: String!, $workspaceSlugs: [String]!, $page: Int, $perPage: Int) {
  pipelines: searchPipelines(
    query: $query
    workspaceSlugs: $workspaceSlugs
    page: $page
    perPage: $perPage
  ) {
    __typename
    ...PipelinesPage
  }
}
    ${PipelinesPageFragmentDoc}`;

/**
 * __useSearchPipelinesQuery__
 *
 * To run a query within a React component, call `useSearchPipelinesQuery` and pass it any options that fit your needs.
 * When your component renders, `useSearchPipelinesQuery` returns an object from Apollo Client that contains loading, error, and data properties
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = useSearchPipelinesQuery({
 *   variables: {
 *      query: // value for 'query'
 *      workspaceSlugs: // value for 'workspaceSlugs'
 *      page: // value for 'page'
 *      perPage: // value for 'perPage'
 *   },
 * });
 */
export function useSearchPipelinesQuery(baseOptions: Apollo.QueryHookOptions<SearchPipelinesQuery, SearchPipelinesQueryVariables> & ({ variables: SearchPipelinesQueryVariables; skip?: boolean; } | { skip: boolean; }) ) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useQuery<SearchPipelinesQuery, SearchPipelinesQueryVariables>(SearchPipelinesDocument, options);
      }
export function useSearchPipelinesLazyQuery(baseOptions?: Apollo.LazyQueryHookOptions<SearchPipelinesQuery, SearchPipelinesQueryVariables>) {
          const options = {...defaultOptions, ...baseOptions}
          return Apollo.useLazyQuery<SearchPipelinesQuery, SearchPipelinesQueryVariables>(SearchPipelinesDocument, options);
        }
export function useSearchPipelinesSuspenseQuery(baseOptions?: Apollo.SkipToken | Apollo.SuspenseQueryHookOptions<SearchPipelinesQuery, SearchPipelinesQueryVariables>) {
          const options = baseOptions === Apollo.skipToken ? baseOptions : {...defaultOptions, ...baseOptions}
          return Apollo.useSuspenseQuery<SearchPipelinesQuery, SearchPipelinesQueryVariables>(SearchPipelinesDocument, options);
        }
export type SearchPipelinesQueryHookResult = ReturnType<typeof useSearchPipelinesQuery>;
export type SearchPipelinesLazyQueryHookResult = ReturnType<typeof useSearchPipelinesLazyQuery>;
export type SearchPipelinesSuspenseQueryHookResult = ReturnType<typeof useSearchPipelinesSuspenseQuery>;
export type SearchPipelinesQueryResult = Apollo.QueryResult<SearchPipelinesQuery, SearchPipelinesQueryVariables>;
export const SearchPipelineTemplatesDocument = gql`
    query SearchPipelineTemplates($query: String!, $workspaceSlugs: [String]!, $page: Int, $perPage: Int) {
  pipelineTemplates: searchPipelineTemplates(
    query: $query
    workspaceSlugs: $workspaceSlugs
    page: $page
    perPage: $perPage
  ) {
    __typename
    ...PipelineTemplatesPage
  }
}
    ${PipelineTemplatesPageFragmentDoc}`;

/**
 * __useSearchPipelineTemplatesQuery__
 *
 * To run a query within a React component, call `useSearchPipelineTemplatesQuery` and pass it any options that fit your needs.
 * When your component renders, `useSearchPipelineTemplatesQuery` returns an object from Apollo Client that contains loading, error, and data properties
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = useSearchPipelineTemplatesQuery({
 *   variables: {
 *      query: // value for 'query'
 *      workspaceSlugs: // value for 'workspaceSlugs'
 *      page: // value for 'page'
 *      perPage: // value for 'perPage'
 *   },
 * });
 */
export function useSearchPipelineTemplatesQuery(baseOptions: Apollo.QueryHookOptions<SearchPipelineTemplatesQuery, SearchPipelineTemplatesQueryVariables> & ({ variables: SearchPipelineTemplatesQueryVariables; skip?: boolean; } | { skip: boolean; }) ) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useQuery<SearchPipelineTemplatesQuery, SearchPipelineTemplatesQueryVariables>(SearchPipelineTemplatesDocument, options);
      }
export function useSearchPipelineTemplatesLazyQuery(baseOptions?: Apollo.LazyQueryHookOptions<SearchPipelineTemplatesQuery, SearchPipelineTemplatesQueryVariables>) {
          const options = {...defaultOptions, ...baseOptions}
          return Apollo.useLazyQuery<SearchPipelineTemplatesQuery, SearchPipelineTemplatesQueryVariables>(SearchPipelineTemplatesDocument, options);
        }
export function useSearchPipelineTemplatesSuspenseQuery(baseOptions?: Apollo.SkipToken | Apollo.SuspenseQueryHookOptions<SearchPipelineTemplatesQuery, SearchPipelineTemplatesQueryVariables>) {
          const options = baseOptions === Apollo.skipToken ? baseOptions : {...defaultOptions, ...baseOptions}
          return Apollo.useSuspenseQuery<SearchPipelineTemplatesQuery, SearchPipelineTemplatesQueryVariables>(SearchPipelineTemplatesDocument, options);
        }
export type SearchPipelineTemplatesQueryHookResult = ReturnType<typeof useSearchPipelineTemplatesQuery>;
export type SearchPipelineTemplatesLazyQueryHookResult = ReturnType<typeof useSearchPipelineTemplatesLazyQuery>;
export type SearchPipelineTemplatesSuspenseQueryHookResult = ReturnType<typeof useSearchPipelineTemplatesSuspenseQuery>;
export type SearchPipelineTemplatesQueryResult = Apollo.QueryResult<SearchPipelineTemplatesQuery, SearchPipelineTemplatesQueryVariables>;
export const SearchDatabaseTablesDocument = gql`
    query SearchDatabaseTables($query: String!, $workspaceSlugs: [String]!, $page: Int, $perPage: Int) {
  databaseTables: searchDatabaseTables(
    query: $query
    workspaceSlugs: $workspaceSlugs
    page: $page
    perPage: $perPage
  ) {
    __typename
    ...DatabaseTablesPage
  }
}
    ${DatabaseTablesPageFragmentDoc}`;

/**
 * __useSearchDatabaseTablesQuery__
 *
 * To run a query within a React component, call `useSearchDatabaseTablesQuery` and pass it any options that fit your needs.
 * When your component renders, `useSearchDatabaseTablesQuery` returns an object from Apollo Client that contains loading, error, and data properties
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = useSearchDatabaseTablesQuery({
 *   variables: {
 *      query: // value for 'query'
 *      workspaceSlugs: // value for 'workspaceSlugs'
 *      page: // value for 'page'
 *      perPage: // value for 'perPage'
 *   },
 * });
 */
export function useSearchDatabaseTablesQuery(baseOptions: Apollo.QueryHookOptions<SearchDatabaseTablesQuery, SearchDatabaseTablesQueryVariables> & ({ variables: SearchDatabaseTablesQueryVariables; skip?: boolean; } | { skip: boolean; }) ) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useQuery<SearchDatabaseTablesQuery, SearchDatabaseTablesQueryVariables>(SearchDatabaseTablesDocument, options);
      }
export function useSearchDatabaseTablesLazyQuery(baseOptions?: Apollo.LazyQueryHookOptions<SearchDatabaseTablesQuery, SearchDatabaseTablesQueryVariables>) {
          const options = {...defaultOptions, ...baseOptions}
          return Apollo.useLazyQuery<SearchDatabaseTablesQuery, SearchDatabaseTablesQueryVariables>(SearchDatabaseTablesDocument, options);
        }
export function useSearchDatabaseTablesSuspenseQuery(baseOptions?: Apollo.SkipToken | Apollo.SuspenseQueryHookOptions<SearchDatabaseTablesQuery, SearchDatabaseTablesQueryVariables>) {
          const options = baseOptions === Apollo.skipToken ? baseOptions : {...defaultOptions, ...baseOptions}
          return Apollo.useSuspenseQuery<SearchDatabaseTablesQuery, SearchDatabaseTablesQueryVariables>(SearchDatabaseTablesDocument, options);
        }
export type SearchDatabaseTablesQueryHookResult = ReturnType<typeof useSearchDatabaseTablesQuery>;
export type SearchDatabaseTablesLazyQueryHookResult = ReturnType<typeof useSearchDatabaseTablesLazyQuery>;
export type SearchDatabaseTablesSuspenseQueryHookResult = ReturnType<typeof useSearchDatabaseTablesSuspenseQuery>;
export type SearchDatabaseTablesQueryResult = Apollo.QueryResult<SearchDatabaseTablesQuery, SearchDatabaseTablesQueryVariables>;
export const SearchFilesDocument = gql`
    query SearchFiles($query: String!, $workspaceSlugs: [String]!, $page: Int, $perPage: Int) {
  files: searchFiles(
    query: $query
    workspaceSlugs: $workspaceSlugs
    page: $page
    perPage: $perPage
  ) {
    __typename
    ...FilesPage
  }
}
    ${FilesPageFragmentDoc}`;

/**
 * __useSearchFilesQuery__
 *
 * To run a query within a React component, call `useSearchFilesQuery` and pass it any options that fit your needs.
 * When your component renders, `useSearchFilesQuery` returns an object from Apollo Client that contains loading, error, and data properties
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = useSearchFilesQuery({
 *   variables: {
 *      query: // value for 'query'
 *      workspaceSlugs: // value for 'workspaceSlugs'
 *      page: // value for 'page'
 *      perPage: // value for 'perPage'
 *   },
 * });
 */
export function useSearchFilesQuery(baseOptions: Apollo.QueryHookOptions<SearchFilesQuery, SearchFilesQueryVariables> & ({ variables: SearchFilesQueryVariables; skip?: boolean; } | { skip: boolean; }) ) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useQuery<SearchFilesQuery, SearchFilesQueryVariables>(SearchFilesDocument, options);
      }
export function useSearchFilesLazyQuery(baseOptions?: Apollo.LazyQueryHookOptions<SearchFilesQuery, SearchFilesQueryVariables>) {
          const options = {...defaultOptions, ...baseOptions}
          return Apollo.useLazyQuery<SearchFilesQuery, SearchFilesQueryVariables>(SearchFilesDocument, options);
        }
export function useSearchFilesSuspenseQuery(baseOptions?: Apollo.SkipToken | Apollo.SuspenseQueryHookOptions<SearchFilesQuery, SearchFilesQueryVariables>) {
          const options = baseOptions === Apollo.skipToken ? baseOptions : {...defaultOptions, ...baseOptions}
          return Apollo.useSuspenseQuery<SearchFilesQuery, SearchFilesQueryVariables>(SearchFilesDocument, options);
        }
export type SearchFilesQueryHookResult = ReturnType<typeof useSearchFilesQuery>;
export type SearchFilesLazyQueryHookResult = ReturnType<typeof useSearchFilesLazyQuery>;
export type SearchFilesSuspenseQueryHookResult = ReturnType<typeof useSearchFilesSuspenseQuery>;
export type SearchFilesQueryResult = Apollo.QueryResult<SearchFilesQuery, SearchFilesQueryVariables>;
export const GetWorkspacesDocument = gql`
    query GetWorkspaces($organizationId: UUID, $page: Int, $perPage: Int) {
  workspaces(organizationId: $organizationId, page: $page, perPage: $perPage) {
    totalItems
    items {
      slug
      ...WorkspaceDisplayFragment
    }
  }
}
    ${WorkspaceDisplayFragmentFragmentDoc}`;

/**
 * __useGetWorkspacesQuery__
 *
 * To run a query within a React component, call `useGetWorkspacesQuery` and pass it any options that fit your needs.
 * When your component renders, `useGetWorkspacesQuery` returns an object from Apollo Client that contains loading, error, and data properties
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = useGetWorkspacesQuery({
 *   variables: {
 *      organizationId: // value for 'organizationId'
 *      page: // value for 'page'
 *      perPage: // value for 'perPage'
 *   },
 * });
 */
export function useGetWorkspacesQuery(baseOptions?: Apollo.QueryHookOptions<GetWorkspacesQuery, GetWorkspacesQueryVariables>) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useQuery<GetWorkspacesQuery, GetWorkspacesQueryVariables>(GetWorkspacesDocument, options);
      }
export function useGetWorkspacesLazyQuery(baseOptions?: Apollo.LazyQueryHookOptions<GetWorkspacesQuery, GetWorkspacesQueryVariables>) {
          const options = {...defaultOptions, ...baseOptions}
          return Apollo.useLazyQuery<GetWorkspacesQuery, GetWorkspacesQueryVariables>(GetWorkspacesDocument, options);
        }
export function useGetWorkspacesSuspenseQuery(baseOptions?: Apollo.SkipToken | Apollo.SuspenseQueryHookOptions<GetWorkspacesQuery, GetWorkspacesQueryVariables>) {
          const options = baseOptions === Apollo.skipToken ? baseOptions : {...defaultOptions, ...baseOptions}
          return Apollo.useSuspenseQuery<GetWorkspacesQuery, GetWorkspacesQueryVariables>(GetWorkspacesDocument, options);
        }
export type GetWorkspacesQueryHookResult = ReturnType<typeof useGetWorkspacesQuery>;
export type GetWorkspacesLazyQueryHookResult = ReturnType<typeof useGetWorkspacesLazyQuery>;
export type GetWorkspacesSuspenseQueryHookResult = ReturnType<typeof useGetWorkspacesSuspenseQuery>;
export type GetWorkspacesQueryResult = Apollo.QueryResult<GetWorkspacesQuery, GetWorkspacesQueryVariables>;
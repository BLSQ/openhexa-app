import * as Types from '../../graphql/types';

import { gql } from '@apollo/client';
import { WorkspaceLayout_WorkspaceFragmentDoc } from '../../workspaces/layouts/WorkspaceLayout/WorkspaceLayout.generated';
import { FilesEditor_FileFragmentDoc } from '../../workspaces/features/FilesEditor/FilesEditor.generated';
import * as Apollo from '@apollo/client';
const defaultOptions = {} as const;
export type SupersetInstancesQueryVariables = Types.Exact<{
  workspaceSlug: Types.Scalars['String']['input'];
}>;


export type SupersetInstancesQuery = { __typename?: 'Query', supersetInstances: Array<{ __typename?: 'SupersetInstance', id: string, name: string, url: string }> };

export type WebappPlay_WebappFragment = { __typename?: 'Webapp', slug: string, url: string, name: string, type: Types.WebappType, showPoweredBy: boolean };

export type WebappAccessQueryVariables = Types.Exact<{
  workspaceSlug: Types.Scalars['String']['input'];
  webappSlug: Types.Scalars['String']['input'];
}>;


export type WebappAccessQuery = { __typename?: 'Query', webapp?: { __typename?: 'Webapp', slug: string, url: string, name: string, type: Types.WebappType, showPoweredBy: boolean, workspace: { __typename?: 'Workspace', slug: string, name: string, permissions: { __typename?: 'WorkspacePermissions', manageMembers: boolean, update: boolean, launchNotebookServer: boolean }, shortcuts: Array<{ __typename?: 'ShortcutItem', id: string, name: string, url: string, order: number }>, countries: Array<{ __typename?: 'Country', flag: string, code: string }>, organization?: { __typename?: 'Organization', id: string, name: string, shortName?: string | null, logo?: string | null, permissions: { __typename?: 'OrganizationPermissions', createWorkspace: { __typename?: 'CreateWorkspacePermission', isAllowed: boolean } } } | null } } | null };

export type WebappVersion_VersionFragment = { __typename?: 'WebappVersion', id: string, message: string, authorName: string, authorEmail: string, date: any };

export type WebappVersionsQueryVariables = Types.Exact<{
  workspaceSlug: Types.Scalars['String']['input'];
  webappSlug: Types.Scalars['String']['input'];
  page?: Types.InputMaybe<Types.Scalars['Int']['input']>;
  perPage?: Types.InputMaybe<Types.Scalars['Int']['input']>;
}>;


export type WebappVersionsQuery = { __typename?: 'Query', webapp?: { __typename?: 'Webapp', id: string, source: { __typename?: 'GitSource', publishedVersion?: string | null } | { __typename?: 'IframeSource' } | { __typename?: 'SupersetSource' }, versions?: { __typename?: 'WebappVersionsPage', page: number, items: Array<{ __typename?: 'WebappVersion', id: string, message: string, authorName: string, authorEmail: string, date: any }> } | null } | null };

export type WebappFilesQueryVariables = Types.Exact<{
  workspaceSlug: Types.Scalars['String']['input'];
  webappSlug: Types.Scalars['String']['input'];
  ref?: Types.InputMaybe<Types.Scalars['String']['input']>;
}>;


export type WebappFilesQuery = { __typename?: 'Query', webapp?: { __typename?: 'Webapp', id: string, files?: Array<{ __typename?: 'FileNode', id: string, name: string, path: string, type: Types.FileType, content?: string | null, parentId?: string | null, autoSelect: boolean, language?: string | null, lineCount?: number | null }> | null } | null };

export const WebappPlay_WebappFragmentDoc = gql`
    fragment WebappPlay_webapp on Webapp {
  slug
  url
  name
  type
  showPoweredBy
}
    `;
export const WebappVersion_VersionFragmentDoc = gql`
    fragment WebappVersion_version on WebappVersion {
  id
  message
  authorName
  authorEmail
  date
}
    `;
export const SupersetInstancesDocument = gql`
    query SupersetInstances($workspaceSlug: String!) {
  supersetInstances(workspaceSlug: $workspaceSlug) {
    id
    name
    url
  }
}
    `;

/**
 * __useSupersetInstancesQuery__
 *
 * To run a query within a React component, call `useSupersetInstancesQuery` and pass it any options that fit your needs.
 * When your component renders, `useSupersetInstancesQuery` returns an object from Apollo Client that contains loading, error, and data properties
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = useSupersetInstancesQuery({
 *   variables: {
 *      workspaceSlug: // value for 'workspaceSlug'
 *   },
 * });
 */
export function useSupersetInstancesQuery(baseOptions: Apollo.QueryHookOptions<SupersetInstancesQuery, SupersetInstancesQueryVariables> & ({ variables: SupersetInstancesQueryVariables; skip?: boolean; } | { skip: boolean; }) ) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useQuery<SupersetInstancesQuery, SupersetInstancesQueryVariables>(SupersetInstancesDocument, options);
      }
export function useSupersetInstancesLazyQuery(baseOptions?: Apollo.LazyQueryHookOptions<SupersetInstancesQuery, SupersetInstancesQueryVariables>) {
          const options = {...defaultOptions, ...baseOptions}
          return Apollo.useLazyQuery<SupersetInstancesQuery, SupersetInstancesQueryVariables>(SupersetInstancesDocument, options);
        }
export function useSupersetInstancesSuspenseQuery(baseOptions?: Apollo.SkipToken | Apollo.SuspenseQueryHookOptions<SupersetInstancesQuery, SupersetInstancesQueryVariables>) {
          const options = baseOptions === Apollo.skipToken ? baseOptions : {...defaultOptions, ...baseOptions}
          return Apollo.useSuspenseQuery<SupersetInstancesQuery, SupersetInstancesQueryVariables>(SupersetInstancesDocument, options);
        }
export type SupersetInstancesQueryHookResult = ReturnType<typeof useSupersetInstancesQuery>;
export type SupersetInstancesLazyQueryHookResult = ReturnType<typeof useSupersetInstancesLazyQuery>;
export type SupersetInstancesSuspenseQueryHookResult = ReturnType<typeof useSupersetInstancesSuspenseQuery>;
export type SupersetInstancesQueryResult = Apollo.QueryResult<SupersetInstancesQuery, SupersetInstancesQueryVariables>;
export const WebappAccessDocument = gql`
    query WebappAccess($workspaceSlug: String!, $webappSlug: String!) {
  webapp(workspaceSlug: $workspaceSlug, slug: $webappSlug) {
    ...WebappPlay_webapp
    workspace {
      ...WorkspaceLayout_workspace
    }
  }
}
    ${WebappPlay_WebappFragmentDoc}
${WorkspaceLayout_WorkspaceFragmentDoc}`;

/**
 * __useWebappAccessQuery__
 *
 * To run a query within a React component, call `useWebappAccessQuery` and pass it any options that fit your needs.
 * When your component renders, `useWebappAccessQuery` returns an object from Apollo Client that contains loading, error, and data properties
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = useWebappAccessQuery({
 *   variables: {
 *      workspaceSlug: // value for 'workspaceSlug'
 *      webappSlug: // value for 'webappSlug'
 *   },
 * });
 */
export function useWebappAccessQuery(baseOptions: Apollo.QueryHookOptions<WebappAccessQuery, WebappAccessQueryVariables> & ({ variables: WebappAccessQueryVariables; skip?: boolean; } | { skip: boolean; }) ) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useQuery<WebappAccessQuery, WebappAccessQueryVariables>(WebappAccessDocument, options);
      }
export function useWebappAccessLazyQuery(baseOptions?: Apollo.LazyQueryHookOptions<WebappAccessQuery, WebappAccessQueryVariables>) {
          const options = {...defaultOptions, ...baseOptions}
          return Apollo.useLazyQuery<WebappAccessQuery, WebappAccessQueryVariables>(WebappAccessDocument, options);
        }
export function useWebappAccessSuspenseQuery(baseOptions?: Apollo.SkipToken | Apollo.SuspenseQueryHookOptions<WebappAccessQuery, WebappAccessQueryVariables>) {
          const options = baseOptions === Apollo.skipToken ? baseOptions : {...defaultOptions, ...baseOptions}
          return Apollo.useSuspenseQuery<WebappAccessQuery, WebappAccessQueryVariables>(WebappAccessDocument, options);
        }
export type WebappAccessQueryHookResult = ReturnType<typeof useWebappAccessQuery>;
export type WebappAccessLazyQueryHookResult = ReturnType<typeof useWebappAccessLazyQuery>;
export type WebappAccessSuspenseQueryHookResult = ReturnType<typeof useWebappAccessSuspenseQuery>;
export type WebappAccessQueryResult = Apollo.QueryResult<WebappAccessQuery, WebappAccessQueryVariables>;
export const WebappVersionsDocument = gql`
    query WebappVersions($workspaceSlug: String!, $webappSlug: String!, $page: Int, $perPage: Int) {
  webapp(workspaceSlug: $workspaceSlug, slug: $webappSlug) {
    id
    source {
      ... on GitSource {
        publishedVersion
      }
    }
    versions(page: $page, perPage: $perPage) {
      items {
        ...WebappVersion_version
      }
      page
    }
  }
}
    ${WebappVersion_VersionFragmentDoc}`;

/**
 * __useWebappVersionsQuery__
 *
 * To run a query within a React component, call `useWebappVersionsQuery` and pass it any options that fit your needs.
 * When your component renders, `useWebappVersionsQuery` returns an object from Apollo Client that contains loading, error, and data properties
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = useWebappVersionsQuery({
 *   variables: {
 *      workspaceSlug: // value for 'workspaceSlug'
 *      webappSlug: // value for 'webappSlug'
 *      page: // value for 'page'
 *      perPage: // value for 'perPage'
 *   },
 * });
 */
export function useWebappVersionsQuery(baseOptions: Apollo.QueryHookOptions<WebappVersionsQuery, WebappVersionsQueryVariables> & ({ variables: WebappVersionsQueryVariables; skip?: boolean; } | { skip: boolean; }) ) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useQuery<WebappVersionsQuery, WebappVersionsQueryVariables>(WebappVersionsDocument, options);
      }
export function useWebappVersionsLazyQuery(baseOptions?: Apollo.LazyQueryHookOptions<WebappVersionsQuery, WebappVersionsQueryVariables>) {
          const options = {...defaultOptions, ...baseOptions}
          return Apollo.useLazyQuery<WebappVersionsQuery, WebappVersionsQueryVariables>(WebappVersionsDocument, options);
        }
export function useWebappVersionsSuspenseQuery(baseOptions?: Apollo.SkipToken | Apollo.SuspenseQueryHookOptions<WebappVersionsQuery, WebappVersionsQueryVariables>) {
          const options = baseOptions === Apollo.skipToken ? baseOptions : {...defaultOptions, ...baseOptions}
          return Apollo.useSuspenseQuery<WebappVersionsQuery, WebappVersionsQueryVariables>(WebappVersionsDocument, options);
        }
export type WebappVersionsQueryHookResult = ReturnType<typeof useWebappVersionsQuery>;
export type WebappVersionsLazyQueryHookResult = ReturnType<typeof useWebappVersionsLazyQuery>;
export type WebappVersionsSuspenseQueryHookResult = ReturnType<typeof useWebappVersionsSuspenseQuery>;
export type WebappVersionsQueryResult = Apollo.QueryResult<WebappVersionsQuery, WebappVersionsQueryVariables>;
export const WebappFilesDocument = gql`
    query WebappFiles($workspaceSlug: String!, $webappSlug: String!, $ref: String) {
  webapp(workspaceSlug: $workspaceSlug, slug: $webappSlug) {
    id
    files(ref: $ref) {
      ...FilesEditor_file
    }
  }
}
    ${FilesEditor_FileFragmentDoc}`;

/**
 * __useWebappFilesQuery__
 *
 * To run a query within a React component, call `useWebappFilesQuery` and pass it any options that fit your needs.
 * When your component renders, `useWebappFilesQuery` returns an object from Apollo Client that contains loading, error, and data properties
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = useWebappFilesQuery({
 *   variables: {
 *      workspaceSlug: // value for 'workspaceSlug'
 *      webappSlug: // value for 'webappSlug'
 *      ref: // value for 'ref'
 *   },
 * });
 */
export function useWebappFilesQuery(baseOptions: Apollo.QueryHookOptions<WebappFilesQuery, WebappFilesQueryVariables> & ({ variables: WebappFilesQueryVariables; skip?: boolean; } | { skip: boolean; }) ) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useQuery<WebappFilesQuery, WebappFilesQueryVariables>(WebappFilesDocument, options);
      }
export function useWebappFilesLazyQuery(baseOptions?: Apollo.LazyQueryHookOptions<WebappFilesQuery, WebappFilesQueryVariables>) {
          const options = {...defaultOptions, ...baseOptions}
          return Apollo.useLazyQuery<WebappFilesQuery, WebappFilesQueryVariables>(WebappFilesDocument, options);
        }
export function useWebappFilesSuspenseQuery(baseOptions?: Apollo.SkipToken | Apollo.SuspenseQueryHookOptions<WebappFilesQuery, WebappFilesQueryVariables>) {
          const options = baseOptions === Apollo.skipToken ? baseOptions : {...defaultOptions, ...baseOptions}
          return Apollo.useSuspenseQuery<WebappFilesQuery, WebappFilesQueryVariables>(WebappFilesDocument, options);
        }
export type WebappFilesQueryHookResult = ReturnType<typeof useWebappFilesQuery>;
export type WebappFilesLazyQueryHookResult = ReturnType<typeof useWebappFilesLazyQuery>;
export type WebappFilesSuspenseQueryHookResult = ReturnType<typeof useWebappFilesSuspenseQuery>;
export type WebappFilesQueryResult = Apollo.QueryResult<WebappFilesQuery, WebappFilesQueryVariables>;
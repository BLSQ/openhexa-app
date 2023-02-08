import * as Types from '../../graphql-types';

import { gql } from '@apollo/client';
import { DeleteWorkspace_WorkspaceFragmentDoc } from '../features/DeleteWorkspaceDialog/DeleteWorkspaceDialog.generated';
import { InviteMemberWorkspace_WorkspaceFragmentDoc } from '../features/InviteMemberDialog/InviteMemberDialog.generated';
import { UpdateWorkspaceDescription_WorkspaceFragmentDoc } from '../features/UpdateDescriptionDialog/UpdateDescriptionDialog.generated';
import * as Apollo from '@apollo/client';
const defaultOptions = {} as const;
export type WorkspacesPageQueryVariables = Types.Exact<{
  page?: Types.InputMaybe<Types.Scalars['Int']>;
  perPage?: Types.InputMaybe<Types.Scalars['Int']>;
}>;


export type WorkspacesPageQuery = { __typename?: 'Query', workspaces: { __typename?: 'WorkspacePage', totalItems: number, items: Array<{ __typename?: 'Workspace', slug: string, name: string, countries: Array<{ __typename?: 'Country', code: string, flag: string }> }> } };

export type WorkspacePageQueryVariables = Types.Exact<{
  slug: Types.Scalars['String'];
}>;


export type WorkspacePageQuery = { __typename?: 'Query', workspace?: { __typename?: 'Workspace', slug: string, name: string, description?: string | null, countries: Array<{ __typename?: 'Country', code: string, flag: string, name: string }>, permissions: { __typename?: 'WorkspacePermissions', delete: boolean, update: boolean, manageMembers: boolean } } | null };

export type WorkspacePipelinesPageQueryVariables = Types.Exact<{
  workspaceSlug: Types.Scalars['String'];
}>;


export type WorkspacePipelinesPageQuery = { __typename?: 'Query', workspace?: { __typename?: 'Workspace', slug: string, name: string } | null };

export type WorkspacePipelinePageQueryVariables = Types.Exact<{
  workspaceSlug: Types.Scalars['String'];
}>;


export type WorkspacePipelinePageQuery = { __typename?: 'Query', workspace?: { __typename?: 'Workspace', slug: string, name: string } | null };

export type WorkspacePipelineStartPageQueryVariables = Types.Exact<{
  workspaceSlug: Types.Scalars['String'];
}>;


export type WorkspacePipelineStartPageQuery = { __typename?: 'Query', workspace?: { __typename?: 'Workspace', slug: string, name: string } | null };

export type WorkspacePipelineRunPageQueryVariables = Types.Exact<{
  workspaceSlug: Types.Scalars['String'];
}>;


export type WorkspacePipelineRunPageQuery = { __typename?: 'Query', workspace?: { __typename?: 'Workspace', slug: string, name: string } | null };

export type WorkspaceFilesPageQueryVariables = Types.Exact<{
  workspaceSlug: Types.Scalars['String'];
}>;


export type WorkspaceFilesPageQuery = { __typename?: 'Query', workspace?: { __typename?: 'Workspace', slug: string, name: string } | null };

export type WorkspaceDatabasesPageQueryVariables = Types.Exact<{
  workspaceSlug: Types.Scalars['String'];
}>;


export type WorkspaceDatabasesPageQuery = { __typename?: 'Query', workspace?: { __typename?: 'Workspace', slug: string, name: string } | null };

export type WorkspaceDatabaseTablePageQueryVariables = Types.Exact<{
  workspaceSlug: Types.Scalars['String'];
}>;


export type WorkspaceDatabaseTablePageQuery = { __typename?: 'Query', workspace?: { __typename?: 'Workspace', slug: string, name: string } | null };

export type WorkspaceConnectionsPageQueryVariables = Types.Exact<{
  workspaceSlug: Types.Scalars['String'];
}>;


export type WorkspaceConnectionsPageQuery = { __typename?: 'Query', workspace?: { __typename?: 'Workspace', slug: string, name: string } | null };

export type WorkspaceConnectionPageQueryVariables = Types.Exact<{
  workspaceSlug: Types.Scalars['String'];
}>;


export type WorkspaceConnectionPageQuery = { __typename?: 'Query', workspace?: { __typename?: 'Workspace', slug: string, name: string } | null };


export const WorkspacesPageDocument = gql`
    query WorkspacesPage($page: Int, $perPage: Int) {
  workspaces(page: $page, perPage: $perPage) {
    totalItems
    items {
      slug
      name
      countries {
        code
        flag
      }
    }
  }
}
    `;

/**
 * __useWorkspacesPageQuery__
 *
 * To run a query within a React component, call `useWorkspacesPageQuery` and pass it any options that fit your needs.
 * When your component renders, `useWorkspacesPageQuery` returns an object from Apollo Client that contains loading, error, and data properties
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = useWorkspacesPageQuery({
 *   variables: {
 *      page: // value for 'page'
 *      perPage: // value for 'perPage'
 *   },
 * });
 */
export function useWorkspacesPageQuery(baseOptions?: Apollo.QueryHookOptions<WorkspacesPageQuery, WorkspacesPageQueryVariables>) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useQuery<WorkspacesPageQuery, WorkspacesPageQueryVariables>(WorkspacesPageDocument, options);
      }
export function useWorkspacesPageLazyQuery(baseOptions?: Apollo.LazyQueryHookOptions<WorkspacesPageQuery, WorkspacesPageQueryVariables>) {
          const options = {...defaultOptions, ...baseOptions}
          return Apollo.useLazyQuery<WorkspacesPageQuery, WorkspacesPageQueryVariables>(WorkspacesPageDocument, options);
        }
export type WorkspacesPageQueryHookResult = ReturnType<typeof useWorkspacesPageQuery>;
export type WorkspacesPageLazyQueryHookResult = ReturnType<typeof useWorkspacesPageLazyQuery>;
export type WorkspacesPageQueryResult = Apollo.QueryResult<WorkspacesPageQuery, WorkspacesPageQueryVariables>;
export const WorkspacePageDocument = gql`
    query WorkspacePage($slug: String!) {
  workspace(slug: $slug) {
    slug
    name
    description
    countries {
      code
      flag
      name
    }
    permissions {
      delete
      update
      manageMembers
    }
    ...DeleteWorkspace_workspace
    ...InviteMemberWorkspace_workspace
    ...UpdateWorkspaceDescription_workspace
  }
}
    ${DeleteWorkspace_WorkspaceFragmentDoc}
${InviteMemberWorkspace_WorkspaceFragmentDoc}
${UpdateWorkspaceDescription_WorkspaceFragmentDoc}`;

/**
 * __useWorkspacePageQuery__
 *
 * To run a query within a React component, call `useWorkspacePageQuery` and pass it any options that fit your needs.
 * When your component renders, `useWorkspacePageQuery` returns an object from Apollo Client that contains loading, error, and data properties
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = useWorkspacePageQuery({
 *   variables: {
 *      slug: // value for 'slug'
 *   },
 * });
 */
export function useWorkspacePageQuery(baseOptions: Apollo.QueryHookOptions<WorkspacePageQuery, WorkspacePageQueryVariables>) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useQuery<WorkspacePageQuery, WorkspacePageQueryVariables>(WorkspacePageDocument, options);
      }
export function useWorkspacePageLazyQuery(baseOptions?: Apollo.LazyQueryHookOptions<WorkspacePageQuery, WorkspacePageQueryVariables>) {
          const options = {...defaultOptions, ...baseOptions}
          return Apollo.useLazyQuery<WorkspacePageQuery, WorkspacePageQueryVariables>(WorkspacePageDocument, options);
        }
export type WorkspacePageQueryHookResult = ReturnType<typeof useWorkspacePageQuery>;
export type WorkspacePageLazyQueryHookResult = ReturnType<typeof useWorkspacePageLazyQuery>;
export type WorkspacePageQueryResult = Apollo.QueryResult<WorkspacePageQuery, WorkspacePageQueryVariables>;
export const WorkspacePipelinesPageDocument = gql`
    query WorkspacePipelinesPage($workspaceSlug: String!) {
  workspace(slug: $workspaceSlug) {
    slug
    name
  }
}
    `;

/**
 * __useWorkspacePipelinesPageQuery__
 *
 * To run a query within a React component, call `useWorkspacePipelinesPageQuery` and pass it any options that fit your needs.
 * When your component renders, `useWorkspacePipelinesPageQuery` returns an object from Apollo Client that contains loading, error, and data properties
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = useWorkspacePipelinesPageQuery({
 *   variables: {
 *      workspaceSlug: // value for 'workspaceSlug'
 *   },
 * });
 */
export function useWorkspacePipelinesPageQuery(baseOptions: Apollo.QueryHookOptions<WorkspacePipelinesPageQuery, WorkspacePipelinesPageQueryVariables>) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useQuery<WorkspacePipelinesPageQuery, WorkspacePipelinesPageQueryVariables>(WorkspacePipelinesPageDocument, options);
      }
export function useWorkspacePipelinesPageLazyQuery(baseOptions?: Apollo.LazyQueryHookOptions<WorkspacePipelinesPageQuery, WorkspacePipelinesPageQueryVariables>) {
          const options = {...defaultOptions, ...baseOptions}
          return Apollo.useLazyQuery<WorkspacePipelinesPageQuery, WorkspacePipelinesPageQueryVariables>(WorkspacePipelinesPageDocument, options);
        }
export type WorkspacePipelinesPageQueryHookResult = ReturnType<typeof useWorkspacePipelinesPageQuery>;
export type WorkspacePipelinesPageLazyQueryHookResult = ReturnType<typeof useWorkspacePipelinesPageLazyQuery>;
export type WorkspacePipelinesPageQueryResult = Apollo.QueryResult<WorkspacePipelinesPageQuery, WorkspacePipelinesPageQueryVariables>;
export const WorkspacePipelinePageDocument = gql`
    query WorkspacePipelinePage($workspaceSlug: String!) {
  workspace(slug: $workspaceSlug) {
    slug
    name
  }
}
    `;

/**
 * __useWorkspacePipelinePageQuery__
 *
 * To run a query within a React component, call `useWorkspacePipelinePageQuery` and pass it any options that fit your needs.
 * When your component renders, `useWorkspacePipelinePageQuery` returns an object from Apollo Client that contains loading, error, and data properties
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = useWorkspacePipelinePageQuery({
 *   variables: {
 *      workspaceSlug: // value for 'workspaceSlug'
 *   },
 * });
 */
export function useWorkspacePipelinePageQuery(baseOptions: Apollo.QueryHookOptions<WorkspacePipelinePageQuery, WorkspacePipelinePageQueryVariables>) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useQuery<WorkspacePipelinePageQuery, WorkspacePipelinePageQueryVariables>(WorkspacePipelinePageDocument, options);
      }
export function useWorkspacePipelinePageLazyQuery(baseOptions?: Apollo.LazyQueryHookOptions<WorkspacePipelinePageQuery, WorkspacePipelinePageQueryVariables>) {
          const options = {...defaultOptions, ...baseOptions}
          return Apollo.useLazyQuery<WorkspacePipelinePageQuery, WorkspacePipelinePageQueryVariables>(WorkspacePipelinePageDocument, options);
        }
export type WorkspacePipelinePageQueryHookResult = ReturnType<typeof useWorkspacePipelinePageQuery>;
export type WorkspacePipelinePageLazyQueryHookResult = ReturnType<typeof useWorkspacePipelinePageLazyQuery>;
export type WorkspacePipelinePageQueryResult = Apollo.QueryResult<WorkspacePipelinePageQuery, WorkspacePipelinePageQueryVariables>;
export const WorkspacePipelineStartPageDocument = gql`
    query WorkspacePipelineStartPage($workspaceSlug: String!) {
  workspace(slug: $workspaceSlug) {
    slug
    name
  }
}
    `;

/**
 * __useWorkspacePipelineStartPageQuery__
 *
 * To run a query within a React component, call `useWorkspacePipelineStartPageQuery` and pass it any options that fit your needs.
 * When your component renders, `useWorkspacePipelineStartPageQuery` returns an object from Apollo Client that contains loading, error, and data properties
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = useWorkspacePipelineStartPageQuery({
 *   variables: {
 *      workspaceSlug: // value for 'workspaceSlug'
 *   },
 * });
 */
export function useWorkspacePipelineStartPageQuery(baseOptions: Apollo.QueryHookOptions<WorkspacePipelineStartPageQuery, WorkspacePipelineStartPageQueryVariables>) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useQuery<WorkspacePipelineStartPageQuery, WorkspacePipelineStartPageQueryVariables>(WorkspacePipelineStartPageDocument, options);
      }
export function useWorkspacePipelineStartPageLazyQuery(baseOptions?: Apollo.LazyQueryHookOptions<WorkspacePipelineStartPageQuery, WorkspacePipelineStartPageQueryVariables>) {
          const options = {...defaultOptions, ...baseOptions}
          return Apollo.useLazyQuery<WorkspacePipelineStartPageQuery, WorkspacePipelineStartPageQueryVariables>(WorkspacePipelineStartPageDocument, options);
        }
export type WorkspacePipelineStartPageQueryHookResult = ReturnType<typeof useWorkspacePipelineStartPageQuery>;
export type WorkspacePipelineStartPageLazyQueryHookResult = ReturnType<typeof useWorkspacePipelineStartPageLazyQuery>;
export type WorkspacePipelineStartPageQueryResult = Apollo.QueryResult<WorkspacePipelineStartPageQuery, WorkspacePipelineStartPageQueryVariables>;
export const WorkspacePipelineRunPageDocument = gql`
    query WorkspacePipelineRunPage($workspaceSlug: String!) {
  workspace(slug: $workspaceSlug) {
    slug
    name
  }
}
    `;

/**
 * __useWorkspacePipelineRunPageQuery__
 *
 * To run a query within a React component, call `useWorkspacePipelineRunPageQuery` and pass it any options that fit your needs.
 * When your component renders, `useWorkspacePipelineRunPageQuery` returns an object from Apollo Client that contains loading, error, and data properties
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = useWorkspacePipelineRunPageQuery({
 *   variables: {
 *      workspaceSlug: // value for 'workspaceSlug'
 *   },
 * });
 */
export function useWorkspacePipelineRunPageQuery(baseOptions: Apollo.QueryHookOptions<WorkspacePipelineRunPageQuery, WorkspacePipelineRunPageQueryVariables>) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useQuery<WorkspacePipelineRunPageQuery, WorkspacePipelineRunPageQueryVariables>(WorkspacePipelineRunPageDocument, options);
      }
export function useWorkspacePipelineRunPageLazyQuery(baseOptions?: Apollo.LazyQueryHookOptions<WorkspacePipelineRunPageQuery, WorkspacePipelineRunPageQueryVariables>) {
          const options = {...defaultOptions, ...baseOptions}
          return Apollo.useLazyQuery<WorkspacePipelineRunPageQuery, WorkspacePipelineRunPageQueryVariables>(WorkspacePipelineRunPageDocument, options);
        }
export type WorkspacePipelineRunPageQueryHookResult = ReturnType<typeof useWorkspacePipelineRunPageQuery>;
export type WorkspacePipelineRunPageLazyQueryHookResult = ReturnType<typeof useWorkspacePipelineRunPageLazyQuery>;
export type WorkspacePipelineRunPageQueryResult = Apollo.QueryResult<WorkspacePipelineRunPageQuery, WorkspacePipelineRunPageQueryVariables>;
export const WorkspaceFilesPageDocument = gql`
    query WorkspaceFilesPage($workspaceSlug: String!) {
  workspace(slug: $workspaceSlug) {
    slug
    name
  }
}
    `;

/**
 * __useWorkspaceFilesPageQuery__
 *
 * To run a query within a React component, call `useWorkspaceFilesPageQuery` and pass it any options that fit your needs.
 * When your component renders, `useWorkspaceFilesPageQuery` returns an object from Apollo Client that contains loading, error, and data properties
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = useWorkspaceFilesPageQuery({
 *   variables: {
 *      workspaceSlug: // value for 'workspaceSlug'
 *   },
 * });
 */
export function useWorkspaceFilesPageQuery(baseOptions: Apollo.QueryHookOptions<WorkspaceFilesPageQuery, WorkspaceFilesPageQueryVariables>) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useQuery<WorkspaceFilesPageQuery, WorkspaceFilesPageQueryVariables>(WorkspaceFilesPageDocument, options);
      }
export function useWorkspaceFilesPageLazyQuery(baseOptions?: Apollo.LazyQueryHookOptions<WorkspaceFilesPageQuery, WorkspaceFilesPageQueryVariables>) {
          const options = {...defaultOptions, ...baseOptions}
          return Apollo.useLazyQuery<WorkspaceFilesPageQuery, WorkspaceFilesPageQueryVariables>(WorkspaceFilesPageDocument, options);
        }
export type WorkspaceFilesPageQueryHookResult = ReturnType<typeof useWorkspaceFilesPageQuery>;
export type WorkspaceFilesPageLazyQueryHookResult = ReturnType<typeof useWorkspaceFilesPageLazyQuery>;
export type WorkspaceFilesPageQueryResult = Apollo.QueryResult<WorkspaceFilesPageQuery, WorkspaceFilesPageQueryVariables>;
export const WorkspaceDatabasesPageDocument = gql`
    query WorkspaceDatabasesPage($workspaceSlug: String!) {
  workspace(slug: $workspaceSlug) {
    slug
    name
  }
}
    `;

/**
 * __useWorkspaceDatabasesPageQuery__
 *
 * To run a query within a React component, call `useWorkspaceDatabasesPageQuery` and pass it any options that fit your needs.
 * When your component renders, `useWorkspaceDatabasesPageQuery` returns an object from Apollo Client that contains loading, error, and data properties
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = useWorkspaceDatabasesPageQuery({
 *   variables: {
 *      workspaceSlug: // value for 'workspaceSlug'
 *   },
 * });
 */
export function useWorkspaceDatabasesPageQuery(baseOptions: Apollo.QueryHookOptions<WorkspaceDatabasesPageQuery, WorkspaceDatabasesPageQueryVariables>) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useQuery<WorkspaceDatabasesPageQuery, WorkspaceDatabasesPageQueryVariables>(WorkspaceDatabasesPageDocument, options);
      }
export function useWorkspaceDatabasesPageLazyQuery(baseOptions?: Apollo.LazyQueryHookOptions<WorkspaceDatabasesPageQuery, WorkspaceDatabasesPageQueryVariables>) {
          const options = {...defaultOptions, ...baseOptions}
          return Apollo.useLazyQuery<WorkspaceDatabasesPageQuery, WorkspaceDatabasesPageQueryVariables>(WorkspaceDatabasesPageDocument, options);
        }
export type WorkspaceDatabasesPageQueryHookResult = ReturnType<typeof useWorkspaceDatabasesPageQuery>;
export type WorkspaceDatabasesPageLazyQueryHookResult = ReturnType<typeof useWorkspaceDatabasesPageLazyQuery>;
export type WorkspaceDatabasesPageQueryResult = Apollo.QueryResult<WorkspaceDatabasesPageQuery, WorkspaceDatabasesPageQueryVariables>;
export const WorkspaceDatabaseTablePageDocument = gql`
    query WorkspaceDatabaseTablePage($workspaceSlug: String!) {
  workspace(slug: $workspaceSlug) {
    slug
    name
  }
}
    `;

/**
 * __useWorkspaceDatabaseTablePageQuery__
 *
 * To run a query within a React component, call `useWorkspaceDatabaseTablePageQuery` and pass it any options that fit your needs.
 * When your component renders, `useWorkspaceDatabaseTablePageQuery` returns an object from Apollo Client that contains loading, error, and data properties
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = useWorkspaceDatabaseTablePageQuery({
 *   variables: {
 *      workspaceSlug: // value for 'workspaceSlug'
 *   },
 * });
 */
export function useWorkspaceDatabaseTablePageQuery(baseOptions: Apollo.QueryHookOptions<WorkspaceDatabaseTablePageQuery, WorkspaceDatabaseTablePageQueryVariables>) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useQuery<WorkspaceDatabaseTablePageQuery, WorkspaceDatabaseTablePageQueryVariables>(WorkspaceDatabaseTablePageDocument, options);
      }
export function useWorkspaceDatabaseTablePageLazyQuery(baseOptions?: Apollo.LazyQueryHookOptions<WorkspaceDatabaseTablePageQuery, WorkspaceDatabaseTablePageQueryVariables>) {
          const options = {...defaultOptions, ...baseOptions}
          return Apollo.useLazyQuery<WorkspaceDatabaseTablePageQuery, WorkspaceDatabaseTablePageQueryVariables>(WorkspaceDatabaseTablePageDocument, options);
        }
export type WorkspaceDatabaseTablePageQueryHookResult = ReturnType<typeof useWorkspaceDatabaseTablePageQuery>;
export type WorkspaceDatabaseTablePageLazyQueryHookResult = ReturnType<typeof useWorkspaceDatabaseTablePageLazyQuery>;
export type WorkspaceDatabaseTablePageQueryResult = Apollo.QueryResult<WorkspaceDatabaseTablePageQuery, WorkspaceDatabaseTablePageQueryVariables>;
export const WorkspaceConnectionsPageDocument = gql`
    query WorkspaceConnectionsPage($workspaceSlug: String!) {
  workspace(slug: $workspaceSlug) {
    slug
    name
  }
}
    `;

/**
 * __useWorkspaceConnectionsPageQuery__
 *
 * To run a query within a React component, call `useWorkspaceConnectionsPageQuery` and pass it any options that fit your needs.
 * When your component renders, `useWorkspaceConnectionsPageQuery` returns an object from Apollo Client that contains loading, error, and data properties
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = useWorkspaceConnectionsPageQuery({
 *   variables: {
 *      workspaceSlug: // value for 'workspaceSlug'
 *   },
 * });
 */
export function useWorkspaceConnectionsPageQuery(baseOptions: Apollo.QueryHookOptions<WorkspaceConnectionsPageQuery, WorkspaceConnectionsPageQueryVariables>) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useQuery<WorkspaceConnectionsPageQuery, WorkspaceConnectionsPageQueryVariables>(WorkspaceConnectionsPageDocument, options);
      }
export function useWorkspaceConnectionsPageLazyQuery(baseOptions?: Apollo.LazyQueryHookOptions<WorkspaceConnectionsPageQuery, WorkspaceConnectionsPageQueryVariables>) {
          const options = {...defaultOptions, ...baseOptions}
          return Apollo.useLazyQuery<WorkspaceConnectionsPageQuery, WorkspaceConnectionsPageQueryVariables>(WorkspaceConnectionsPageDocument, options);
        }
export type WorkspaceConnectionsPageQueryHookResult = ReturnType<typeof useWorkspaceConnectionsPageQuery>;
export type WorkspaceConnectionsPageLazyQueryHookResult = ReturnType<typeof useWorkspaceConnectionsPageLazyQuery>;
export type WorkspaceConnectionsPageQueryResult = Apollo.QueryResult<WorkspaceConnectionsPageQuery, WorkspaceConnectionsPageQueryVariables>;
export const WorkspaceConnectionPageDocument = gql`
    query WorkspaceConnectionPage($workspaceSlug: String!) {
  workspace(slug: $workspaceSlug) {
    slug
    name
  }
}
    `;

/**
 * __useWorkspaceConnectionPageQuery__
 *
 * To run a query within a React component, call `useWorkspaceConnectionPageQuery` and pass it any options that fit your needs.
 * When your component renders, `useWorkspaceConnectionPageQuery` returns an object from Apollo Client that contains loading, error, and data properties
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = useWorkspaceConnectionPageQuery({
 *   variables: {
 *      workspaceSlug: // value for 'workspaceSlug'
 *   },
 * });
 */
export function useWorkspaceConnectionPageQuery(baseOptions: Apollo.QueryHookOptions<WorkspaceConnectionPageQuery, WorkspaceConnectionPageQueryVariables>) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useQuery<WorkspaceConnectionPageQuery, WorkspaceConnectionPageQueryVariables>(WorkspaceConnectionPageDocument, options);
      }
export function useWorkspaceConnectionPageLazyQuery(baseOptions?: Apollo.LazyQueryHookOptions<WorkspaceConnectionPageQuery, WorkspaceConnectionPageQueryVariables>) {
          const options = {...defaultOptions, ...baseOptions}
          return Apollo.useLazyQuery<WorkspaceConnectionPageQuery, WorkspaceConnectionPageQueryVariables>(WorkspaceConnectionPageDocument, options);
        }
export type WorkspaceConnectionPageQueryHookResult = ReturnType<typeof useWorkspaceConnectionPageQuery>;
export type WorkspaceConnectionPageLazyQueryHookResult = ReturnType<typeof useWorkspaceConnectionPageLazyQuery>;
export type WorkspaceConnectionPageQueryResult = Apollo.QueryResult<WorkspaceConnectionPageQuery, WorkspaceConnectionPageQueryVariables>;
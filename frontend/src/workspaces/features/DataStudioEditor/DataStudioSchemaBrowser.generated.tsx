import * as Types from '../../../graphql/types';

import { gql } from '@apollo/client';
import * as Apollo from '@apollo/client';
const defaultOptions = {} as const;
export type WorkspaceDataStudioSchemaQueryVariables = Types.Exact<{
  workspaceSlug: Types.Scalars['String']['input'];
}>;


export type WorkspaceDataStudioSchemaQuery = { __typename?: 'Query', workspace?: { __typename?: 'Workspace', slug: string, database: { __typename?: 'Database', tables: { __typename?: 'DatabaseTablePage', totalItems: number, items: Array<{ __typename?: 'DatabaseTable', name: string }> } } } | null };

export type WorkspaceDataStudioTableColumnsQueryVariables = Types.Exact<{
  workspaceSlug: Types.Scalars['String']['input'];
  table: Types.Scalars['String']['input'];
}>;


export type WorkspaceDataStudioTableColumnsQuery = { __typename?: 'Query', workspace?: { __typename?: 'Workspace', slug: string, database: { __typename?: 'Database', table?: { __typename?: 'DatabaseTable', name: string, columns: Array<{ __typename?: 'TableColumn', name: string, type: string }> } | null } } | null };


export const WorkspaceDataStudioSchemaDocument = gql`
    query WorkspaceDataStudioSchema($workspaceSlug: String!) {
  workspace(slug: $workspaceSlug) {
    slug
    database {
      tables(page: 1, perPage: 100) {
        totalItems
        items {
          name
        }
      }
    }
  }
}
    `;

/**
 * __useWorkspaceDataStudioSchemaQuery__
 *
 * To run a query within a React component, call `useWorkspaceDataStudioSchemaQuery` and pass it any options that fit your needs.
 * When your component renders, `useWorkspaceDataStudioSchemaQuery` returns an object from Apollo Client that contains loading, error, and data properties
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = useWorkspaceDataStudioSchemaQuery({
 *   variables: {
 *      workspaceSlug: // value for 'workspaceSlug'
 *   },
 * });
 */
export function useWorkspaceDataStudioSchemaQuery(baseOptions: Apollo.QueryHookOptions<WorkspaceDataStudioSchemaQuery, WorkspaceDataStudioSchemaQueryVariables> & ({ variables: WorkspaceDataStudioSchemaQueryVariables; skip?: boolean; } | { skip: boolean; }) ) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useQuery<WorkspaceDataStudioSchemaQuery, WorkspaceDataStudioSchemaQueryVariables>(WorkspaceDataStudioSchemaDocument, options);
      }
export function useWorkspaceDataStudioSchemaLazyQuery(baseOptions?: Apollo.LazyQueryHookOptions<WorkspaceDataStudioSchemaQuery, WorkspaceDataStudioSchemaQueryVariables>) {
          const options = {...defaultOptions, ...baseOptions}
          return Apollo.useLazyQuery<WorkspaceDataStudioSchemaQuery, WorkspaceDataStudioSchemaQueryVariables>(WorkspaceDataStudioSchemaDocument, options);
        }
export function useWorkspaceDataStudioSchemaSuspenseQuery(baseOptions?: Apollo.SkipToken | Apollo.SuspenseQueryHookOptions<WorkspaceDataStudioSchemaQuery, WorkspaceDataStudioSchemaQueryVariables>) {
          const options = baseOptions === Apollo.skipToken ? baseOptions : {...defaultOptions, ...baseOptions}
          return Apollo.useSuspenseQuery<WorkspaceDataStudioSchemaQuery, WorkspaceDataStudioSchemaQueryVariables>(WorkspaceDataStudioSchemaDocument, options);
        }
export type WorkspaceDataStudioSchemaQueryHookResult = ReturnType<typeof useWorkspaceDataStudioSchemaQuery>;
export type WorkspaceDataStudioSchemaLazyQueryHookResult = ReturnType<typeof useWorkspaceDataStudioSchemaLazyQuery>;
export type WorkspaceDataStudioSchemaSuspenseQueryHookResult = ReturnType<typeof useWorkspaceDataStudioSchemaSuspenseQuery>;
export type WorkspaceDataStudioSchemaQueryResult = Apollo.QueryResult<WorkspaceDataStudioSchemaQuery, WorkspaceDataStudioSchemaQueryVariables>;
export const WorkspaceDataStudioTableColumnsDocument = gql`
    query WorkspaceDataStudioTableColumns($workspaceSlug: String!, $table: String!) {
  workspace(slug: $workspaceSlug) {
    slug
    database {
      table(name: $table) {
        name
        columns {
          name
          type
        }
      }
    }
  }
}
    `;

/**
 * __useWorkspaceDataStudioTableColumnsQuery__
 *
 * To run a query within a React component, call `useWorkspaceDataStudioTableColumnsQuery` and pass it any options that fit your needs.
 * When your component renders, `useWorkspaceDataStudioTableColumnsQuery` returns an object from Apollo Client that contains loading, error, and data properties
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = useWorkspaceDataStudioTableColumnsQuery({
 *   variables: {
 *      workspaceSlug: // value for 'workspaceSlug'
 *      table: // value for 'table'
 *   },
 * });
 */
export function useWorkspaceDataStudioTableColumnsQuery(baseOptions: Apollo.QueryHookOptions<WorkspaceDataStudioTableColumnsQuery, WorkspaceDataStudioTableColumnsQueryVariables> & ({ variables: WorkspaceDataStudioTableColumnsQueryVariables; skip?: boolean; } | { skip: boolean; }) ) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useQuery<WorkspaceDataStudioTableColumnsQuery, WorkspaceDataStudioTableColumnsQueryVariables>(WorkspaceDataStudioTableColumnsDocument, options);
      }
export function useWorkspaceDataStudioTableColumnsLazyQuery(baseOptions?: Apollo.LazyQueryHookOptions<WorkspaceDataStudioTableColumnsQuery, WorkspaceDataStudioTableColumnsQueryVariables>) {
          const options = {...defaultOptions, ...baseOptions}
          return Apollo.useLazyQuery<WorkspaceDataStudioTableColumnsQuery, WorkspaceDataStudioTableColumnsQueryVariables>(WorkspaceDataStudioTableColumnsDocument, options);
        }
export function useWorkspaceDataStudioTableColumnsSuspenseQuery(baseOptions?: Apollo.SkipToken | Apollo.SuspenseQueryHookOptions<WorkspaceDataStudioTableColumnsQuery, WorkspaceDataStudioTableColumnsQueryVariables>) {
          const options = baseOptions === Apollo.skipToken ? baseOptions : {...defaultOptions, ...baseOptions}
          return Apollo.useSuspenseQuery<WorkspaceDataStudioTableColumnsQuery, WorkspaceDataStudioTableColumnsQueryVariables>(WorkspaceDataStudioTableColumnsDocument, options);
        }
export type WorkspaceDataStudioTableColumnsQueryHookResult = ReturnType<typeof useWorkspaceDataStudioTableColumnsQuery>;
export type WorkspaceDataStudioTableColumnsLazyQueryHookResult = ReturnType<typeof useWorkspaceDataStudioTableColumnsLazyQuery>;
export type WorkspaceDataStudioTableColumnsSuspenseQueryHookResult = ReturnType<typeof useWorkspaceDataStudioTableColumnsSuspenseQuery>;
export type WorkspaceDataStudioTableColumnsQueryResult = Apollo.QueryResult<WorkspaceDataStudioTableColumnsQuery, WorkspaceDataStudioTableColumnsQueryVariables>;
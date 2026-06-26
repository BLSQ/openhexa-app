import * as Types from '../../../graphql/types';

import { gql } from '@apollo/client';
import * as Apollo from '@apollo/client';
const defaultOptions = {} as const;
export type WorkspaceDataStudioSchemaQueryVariables = Types.Exact<{
  workspaceSlug: Types.Scalars['String']['input'];
}>;


export type WorkspaceDataStudioSchemaQuery = { __typename?: 'Query', workspace?: { __typename?: 'Workspace', slug: string, database: { __typename?: 'Database', tables: { __typename?: 'DatabaseTablePage', totalItems: number, items: Array<{ __typename?: 'DatabaseTable', name: string, columns: Array<{ __typename?: 'TableColumn', name: string, type: string }> }> } } } | null };


export const WorkspaceDataStudioSchemaDocument = gql`
    query WorkspaceDataStudioSchema($workspaceSlug: String!) {
  workspace(slug: $workspaceSlug) {
    slug
    database {
      tables(page: 1, perPage: 100) {
        totalItems
        items {
          name
          columns {
            name
            type
          }
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
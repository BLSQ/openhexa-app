import * as Types from '../../../graphql-types';

import { gql } from '@apollo/client';
import * as Apollo from '@apollo/client';
const defaultOptions = {} as const;
export type WorkspaceDatabaseTableDataQueryVariables = Types.Exact<{
  workspaceSlug: Types.Scalars['String'];
  tableName: Types.Scalars['String'];
}>;


export type WorkspaceDatabaseTableDataQuery = { __typename?: 'Query', workspace?: { __typename?: 'Workspace', slug: string, database: { __typename?: 'Database', table?: { __typename?: 'DatabaseTable', sample: any, columns: Array<{ __typename?: 'TableColumn', name: string, type: string }> } | null } } | null };


export const WorkspaceDatabaseTableDataDocument = gql`
    query WorkspaceDatabaseTableData($workspaceSlug: String!, $tableName: String!) {
  workspace(slug: $workspaceSlug) {
    slug
    database {
      table(name: $tableName) {
        columns {
          name
          type
        }
        sample
      }
    }
  }
}
    `;

/**
 * __useWorkspaceDatabaseTableDataQuery__
 *
 * To run a query within a React component, call `useWorkspaceDatabaseTableDataQuery` and pass it any options that fit your needs.
 * When your component renders, `useWorkspaceDatabaseTableDataQuery` returns an object from Apollo Client that contains loading, error, and data properties
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = useWorkspaceDatabaseTableDataQuery({
 *   variables: {
 *      workspaceSlug: // value for 'workspaceSlug'
 *      tableName: // value for 'tableName'
 *   },
 * });
 */
export function useWorkspaceDatabaseTableDataQuery(baseOptions: Apollo.QueryHookOptions<WorkspaceDatabaseTableDataQuery, WorkspaceDatabaseTableDataQueryVariables>) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useQuery<WorkspaceDatabaseTableDataQuery, WorkspaceDatabaseTableDataQueryVariables>(WorkspaceDatabaseTableDataDocument, options);
      }
export function useWorkspaceDatabaseTableDataLazyQuery(baseOptions?: Apollo.LazyQueryHookOptions<WorkspaceDatabaseTableDataQuery, WorkspaceDatabaseTableDataQueryVariables>) {
          const options = {...defaultOptions, ...baseOptions}
          return Apollo.useLazyQuery<WorkspaceDatabaseTableDataQuery, WorkspaceDatabaseTableDataQueryVariables>(WorkspaceDatabaseTableDataDocument, options);
        }
export type WorkspaceDatabaseTableDataQueryHookResult = ReturnType<typeof useWorkspaceDatabaseTableDataQuery>;
export type WorkspaceDatabaseTableDataLazyQueryHookResult = ReturnType<typeof useWorkspaceDatabaseTableDataLazyQuery>;
export type WorkspaceDatabaseTableDataQueryResult = Apollo.QueryResult<WorkspaceDatabaseTableDataQuery, WorkspaceDatabaseTableDataQueryVariables>;
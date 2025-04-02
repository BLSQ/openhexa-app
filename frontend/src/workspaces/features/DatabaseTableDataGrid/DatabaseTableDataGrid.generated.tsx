import * as Types from '../../../graphql/types';

import { gql } from '@apollo/client';
import * as Apollo from '@apollo/client';
const defaultOptions = {} as const;
export type DatabaseTableDataGridQueryVariables = Types.Exact<{
  workspaceSlug: Types.Scalars['String']['input'];
  tableName: Types.Scalars['String']['input'];
  orderBy: Types.Scalars['String']['input'];
  direction: Types.OrderByDirection;
  page: Types.Scalars['Int']['input'];
}>;


export type DatabaseTableDataGridQuery = { __typename?: 'Query', workspace?: { __typename?: 'Workspace', slug: string, database: { __typename?: 'Database', table?: { __typename?: 'DatabaseTable', rows: { __typename?: 'TableRowsPage', pageNumber: number, hasNextPage: boolean, hasPreviousPage: boolean, items: Array<any> } } | null } } | null };

export type DatabaseTableDataGrid_WorkspaceFragment = { __typename?: 'Workspace', slug: string };

export type DatabaseTableDataGrid_TableFragment = { __typename?: 'DatabaseTable', name: string, columns: Array<{ __typename?: 'TableColumn', name: string }> };

export const DatabaseTableDataGrid_WorkspaceFragmentDoc = gql`
    fragment DatabaseTableDataGrid_workspace on Workspace {
  slug
}
    `;
export const DatabaseTableDataGrid_TableFragmentDoc = gql`
    fragment DatabaseTableDataGrid_table on DatabaseTable {
  name
  columns {
    name
  }
}
    `;
export const DatabaseTableDataGridDocument = gql`
    query DatabaseTableDataGrid($workspaceSlug: String!, $tableName: String!, $orderBy: String!, $direction: OrderByDirection!, $page: Int!) {
  workspace(slug: $workspaceSlug) {
    slug
    database {
      table(name: $tableName) {
        rows(orderBy: $orderBy, direction: $direction, page: $page, perPage: 10) {
          pageNumber
          hasNextPage
          hasPreviousPage
          items
        }
      }
    }
  }
}
    `;

/**
 * __useDatabaseTableDataGridQuery__
 *
 * To run a query within a React component, call `useDatabaseTableDataGridQuery` and pass it any options that fit your needs.
 * When your component renders, `useDatabaseTableDataGridQuery` returns an object from Apollo Client that contains loading, error, and data properties
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = useDatabaseTableDataGridQuery({
 *   variables: {
 *      workspaceSlug: // value for 'workspaceSlug'
 *      tableName: // value for 'tableName'
 *      orderBy: // value for 'orderBy'
 *      direction: // value for 'direction'
 *      page: // value for 'page'
 *   },
 * });
 */
export function useDatabaseTableDataGridQuery(baseOptions: Apollo.QueryHookOptions<DatabaseTableDataGridQuery, DatabaseTableDataGridQueryVariables> & ({ variables: DatabaseTableDataGridQueryVariables; skip?: boolean; } | { skip: boolean; }) ) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useQuery<DatabaseTableDataGridQuery, DatabaseTableDataGridQueryVariables>(DatabaseTableDataGridDocument, options);
      }
export function useDatabaseTableDataGridLazyQuery(baseOptions?: Apollo.LazyQueryHookOptions<DatabaseTableDataGridQuery, DatabaseTableDataGridQueryVariables>) {
          const options = {...defaultOptions, ...baseOptions}
          return Apollo.useLazyQuery<DatabaseTableDataGridQuery, DatabaseTableDataGridQueryVariables>(DatabaseTableDataGridDocument, options);
        }
export function useDatabaseTableDataGridSuspenseQuery(baseOptions?: Apollo.SkipToken | Apollo.SuspenseQueryHookOptions<DatabaseTableDataGridQuery, DatabaseTableDataGridQueryVariables>) {
          const options = baseOptions === Apollo.skipToken ? baseOptions : {...defaultOptions, ...baseOptions}
          return Apollo.useSuspenseQuery<DatabaseTableDataGridQuery, DatabaseTableDataGridQueryVariables>(DatabaseTableDataGridDocument, options);
        }
export type DatabaseTableDataGridQueryHookResult = ReturnType<typeof useDatabaseTableDataGridQuery>;
export type DatabaseTableDataGridLazyQueryHookResult = ReturnType<typeof useDatabaseTableDataGridLazyQuery>;
export type DatabaseTableDataGridSuspenseQueryHookResult = ReturnType<typeof useDatabaseTableDataGridSuspenseQuery>;
export type DatabaseTableDataGridQueryResult = Apollo.QueryResult<DatabaseTableDataGridQuery, DatabaseTableDataGridQueryVariables>;
import * as Types from '../../../graphql/types';

import { gql } from '@apollo/client';
import * as Apollo from '@apollo/client';
const defaultOptions = {} as const;
export type ExecuteWorkspaceSqlQueryVariables = Types.Exact<{
  workspaceSlug: Types.Scalars['String']['input'];
  query: Types.Scalars['String']['input'];
  maxRows?: Types.InputMaybe<Types.Scalars['Int']['input']>;
}>;


export type ExecuteWorkspaceSqlQuery = { __typename?: 'Query', workspace?: { __typename?: 'Workspace', slug: string, database: { __typename?: 'Database', executeSQL: { __typename?: 'ExecuteSQLResult', success: boolean, errors: Array<Types.ExecuteSqlError>, errorMessage?: string | null, columns?: Array<string> | null, rows?: Array<any> | null, rowCount?: number | null, truncated?: boolean | null } } } | null };


export const ExecuteWorkspaceSqlDocument = gql`
    query ExecuteWorkspaceSql($workspaceSlug: String!, $query: String!, $maxRows: Int) {
  workspace(slug: $workspaceSlug) {
    slug
    database {
      executeSQL(query: $query, maxRows: $maxRows) {
        success
        errors
        errorMessage
        columns
        rows
        rowCount
        truncated
      }
    }
  }
}
    `;

/**
 * __useExecuteWorkspaceSqlQuery__
 *
 * To run a query within a React component, call `useExecuteWorkspaceSqlQuery` and pass it any options that fit your needs.
 * When your component renders, `useExecuteWorkspaceSqlQuery` returns an object from Apollo Client that contains loading, error, and data properties
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = useExecuteWorkspaceSqlQuery({
 *   variables: {
 *      workspaceSlug: // value for 'workspaceSlug'
 *      query: // value for 'query'
 *      maxRows: // value for 'maxRows'
 *   },
 * });
 */
export function useExecuteWorkspaceSqlQuery(baseOptions: Apollo.QueryHookOptions<ExecuteWorkspaceSqlQuery, ExecuteWorkspaceSqlQueryVariables> & ({ variables: ExecuteWorkspaceSqlQueryVariables; skip?: boolean; } | { skip: boolean; }) ) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useQuery<ExecuteWorkspaceSqlQuery, ExecuteWorkspaceSqlQueryVariables>(ExecuteWorkspaceSqlDocument, options);
      }
export function useExecuteWorkspaceSqlLazyQuery(baseOptions?: Apollo.LazyQueryHookOptions<ExecuteWorkspaceSqlQuery, ExecuteWorkspaceSqlQueryVariables>) {
          const options = {...defaultOptions, ...baseOptions}
          return Apollo.useLazyQuery<ExecuteWorkspaceSqlQuery, ExecuteWorkspaceSqlQueryVariables>(ExecuteWorkspaceSqlDocument, options);
        }
export function useExecuteWorkspaceSqlSuspenseQuery(baseOptions?: Apollo.SkipToken | Apollo.SuspenseQueryHookOptions<ExecuteWorkspaceSqlQuery, ExecuteWorkspaceSqlQueryVariables>) {
          const options = baseOptions === Apollo.skipToken ? baseOptions : {...defaultOptions, ...baseOptions}
          return Apollo.useSuspenseQuery<ExecuteWorkspaceSqlQuery, ExecuteWorkspaceSqlQueryVariables>(ExecuteWorkspaceSqlDocument, options);
        }
export type ExecuteWorkspaceSqlQueryHookResult = ReturnType<typeof useExecuteWorkspaceSqlQuery>;
export type ExecuteWorkspaceSqlLazyQueryHookResult = ReturnType<typeof useExecuteWorkspaceSqlLazyQuery>;
export type ExecuteWorkspaceSqlSuspenseQueryHookResult = ReturnType<typeof useExecuteWorkspaceSqlSuspenseQuery>;
export type ExecuteWorkspaceSqlQueryResult = Apollo.QueryResult<ExecuteWorkspaceSqlQuery, ExecuteWorkspaceSqlQueryVariables>;
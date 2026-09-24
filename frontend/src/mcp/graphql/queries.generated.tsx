import * as Types from '../../graphql/types';

import { gql } from '@apollo/client';
import * as Apollo from '@apollo/client';
const defaultOptions = {} as const;
export type McpConnection_ConnectionFragment = { __typename?: 'MCPConnection', id: string, name: string, createdAt: any, lastUsedAt?: any | null, tools: Array<string>, workspaces: Array<{ __typename?: 'Workspace', slug: string, name: string }> };

export type AccountMcpConnectionsQueryVariables = Types.Exact<{
  page?: Types.InputMaybe<Types.Scalars['Int']['input']>;
  perPage?: Types.InputMaybe<Types.Scalars['Int']['input']>;
}>;


export type AccountMcpConnectionsQuery = { __typename?: 'Query', mcpConnections: Array<{ __typename?: 'MCPConnection', id: string, name: string, createdAt: any, lastUsedAt?: any | null, tools: Array<string>, workspaces: Array<{ __typename?: 'Workspace', slug: string, name: string }> }>, mcpTools: Array<{ __typename?: 'MCPTool', name: string, description: string, resource?: Types.McpResource | null, write: boolean }>, workspaces: { __typename?: 'WorkspacePage', totalItems: number, items: Array<{ __typename?: 'Workspace', slug: string, name: string, countries: Array<{ __typename?: 'Country', code: string }> }> } };

export type McpAuthorizationRequestQueryVariables = Types.Exact<{
  clientId: Types.Scalars['String']['input'];
  page?: Types.InputMaybe<Types.Scalars['Int']['input']>;
  perPage?: Types.InputMaybe<Types.Scalars['Int']['input']>;
}>;


export type McpAuthorizationRequestQuery = { __typename?: 'Query', mcpAuthorizationRequest?: { __typename?: 'MCPAuthorizationRequest', clientName: string, connection?: { __typename?: 'MCPConnection', id: string, name: string, createdAt: any, lastUsedAt?: any | null, tools: Array<string>, workspaces: Array<{ __typename?: 'Workspace', slug: string, name: string }> } | null, tools: Array<{ __typename?: 'MCPTool', name: string, description: string, resource?: Types.McpResource | null, write: boolean }> } | null, workspaces: { __typename?: 'WorkspacePage', totalItems: number, items: Array<{ __typename?: 'Workspace', slug: string, name: string, countries: Array<{ __typename?: 'Country', code: string }> }> } };

export const McpConnection_ConnectionFragmentDoc = gql`
    fragment MCPConnection_connection on MCPConnection {
  id
  name
  createdAt
  lastUsedAt
  workspaces {
    slug
    name
  }
  tools
}
    `;
export const AccountMcpConnectionsDocument = gql`
    query AccountMCPConnections($page: Int, $perPage: Int) {
  mcpConnections {
    ...MCPConnection_connection
  }
  mcpTools {
    name
    description
    resource
    write
  }
  workspaces(page: $page, perPage: $perPage) {
    totalItems
    items {
      slug
      name
      countries {
        code
      }
    }
  }
}
    ${McpConnection_ConnectionFragmentDoc}`;

/**
 * __useAccountMcpConnectionsQuery__
 *
 * To run a query within a React component, call `useAccountMcpConnectionsQuery` and pass it any options that fit your needs.
 * When your component renders, `useAccountMcpConnectionsQuery` returns an object from Apollo Client that contains loading, error, and data properties
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = useAccountMcpConnectionsQuery({
 *   variables: {
 *      page: // value for 'page'
 *      perPage: // value for 'perPage'
 *   },
 * });
 */
export function useAccountMcpConnectionsQuery(baseOptions?: Apollo.QueryHookOptions<AccountMcpConnectionsQuery, AccountMcpConnectionsQueryVariables>) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useQuery<AccountMcpConnectionsQuery, AccountMcpConnectionsQueryVariables>(AccountMcpConnectionsDocument, options);
      }
export function useAccountMcpConnectionsLazyQuery(baseOptions?: Apollo.LazyQueryHookOptions<AccountMcpConnectionsQuery, AccountMcpConnectionsQueryVariables>) {
          const options = {...defaultOptions, ...baseOptions}
          return Apollo.useLazyQuery<AccountMcpConnectionsQuery, AccountMcpConnectionsQueryVariables>(AccountMcpConnectionsDocument, options);
        }
export function useAccountMcpConnectionsSuspenseQuery(baseOptions?: Apollo.SkipToken | Apollo.SuspenseQueryHookOptions<AccountMcpConnectionsQuery, AccountMcpConnectionsQueryVariables>) {
          const options = baseOptions === Apollo.skipToken ? baseOptions : {...defaultOptions, ...baseOptions}
          return Apollo.useSuspenseQuery<AccountMcpConnectionsQuery, AccountMcpConnectionsQueryVariables>(AccountMcpConnectionsDocument, options);
        }
export type AccountMcpConnectionsQueryHookResult = ReturnType<typeof useAccountMcpConnectionsQuery>;
export type AccountMcpConnectionsLazyQueryHookResult = ReturnType<typeof useAccountMcpConnectionsLazyQuery>;
export type AccountMcpConnectionsSuspenseQueryHookResult = ReturnType<typeof useAccountMcpConnectionsSuspenseQuery>;
export type AccountMcpConnectionsQueryResult = Apollo.QueryResult<AccountMcpConnectionsQuery, AccountMcpConnectionsQueryVariables>;
export const McpAuthorizationRequestDocument = gql`
    query MCPAuthorizationRequest($clientId: String!, $page: Int, $perPage: Int) {
  mcpAuthorizationRequest(clientId: $clientId) {
    clientName
    connection {
      ...MCPConnection_connection
    }
    tools {
      name
      description
      resource
      write
    }
  }
  workspaces(page: $page, perPage: $perPage) {
    totalItems
    items {
      slug
      name
      countries {
        code
      }
    }
  }
}
    ${McpConnection_ConnectionFragmentDoc}`;

/**
 * __useMcpAuthorizationRequestQuery__
 *
 * To run a query within a React component, call `useMcpAuthorizationRequestQuery` and pass it any options that fit your needs.
 * When your component renders, `useMcpAuthorizationRequestQuery` returns an object from Apollo Client that contains loading, error, and data properties
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = useMcpAuthorizationRequestQuery({
 *   variables: {
 *      clientId: // value for 'clientId'
 *      page: // value for 'page'
 *      perPage: // value for 'perPage'
 *   },
 * });
 */
export function useMcpAuthorizationRequestQuery(baseOptions: Apollo.QueryHookOptions<McpAuthorizationRequestQuery, McpAuthorizationRequestQueryVariables> & ({ variables: McpAuthorizationRequestQueryVariables; skip?: boolean; } | { skip: boolean; }) ) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useQuery<McpAuthorizationRequestQuery, McpAuthorizationRequestQueryVariables>(McpAuthorizationRequestDocument, options);
      }
export function useMcpAuthorizationRequestLazyQuery(baseOptions?: Apollo.LazyQueryHookOptions<McpAuthorizationRequestQuery, McpAuthorizationRequestQueryVariables>) {
          const options = {...defaultOptions, ...baseOptions}
          return Apollo.useLazyQuery<McpAuthorizationRequestQuery, McpAuthorizationRequestQueryVariables>(McpAuthorizationRequestDocument, options);
        }
export function useMcpAuthorizationRequestSuspenseQuery(baseOptions?: Apollo.SkipToken | Apollo.SuspenseQueryHookOptions<McpAuthorizationRequestQuery, McpAuthorizationRequestQueryVariables>) {
          const options = baseOptions === Apollo.skipToken ? baseOptions : {...defaultOptions, ...baseOptions}
          return Apollo.useSuspenseQuery<McpAuthorizationRequestQuery, McpAuthorizationRequestQueryVariables>(McpAuthorizationRequestDocument, options);
        }
export type McpAuthorizationRequestQueryHookResult = ReturnType<typeof useMcpAuthorizationRequestQuery>;
export type McpAuthorizationRequestLazyQueryHookResult = ReturnType<typeof useMcpAuthorizationRequestLazyQuery>;
export type McpAuthorizationRequestSuspenseQueryHookResult = ReturnType<typeof useMcpAuthorizationRequestSuspenseQuery>;
export type McpAuthorizationRequestQueryResult = Apollo.QueryResult<McpAuthorizationRequestQuery, McpAuthorizationRequestQueryVariables>;
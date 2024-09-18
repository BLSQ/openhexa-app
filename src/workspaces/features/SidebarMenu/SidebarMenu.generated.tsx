import * as Types from '../../../graphql/types';

import { gql } from '@apollo/client';
import * as Apollo from '@apollo/client';
const defaultOptions = {} as const;
export type SidebarMenuQueryVariables = Types.Exact<{
  page?: Types.InputMaybe<Types.Scalars['Int']['input']>;
  perPage?: Types.InputMaybe<Types.Scalars['Int']['input']>;
}>;


export type SidebarMenuQuery = { __typename?: 'Query', pendingWorkspaceInvitations: { __typename?: 'WorkspaceInvitationPage', totalItems: number }, workspaces: { __typename?: 'WorkspacePage', totalItems: number, items: Array<{ __typename?: 'Workspace', slug: string, name: string, countries: Array<{ __typename?: 'Country', code: string, flag: string }> }> } };

export type SidebarMenu_WorkspaceFragment = { __typename?: 'Workspace', slug: string, name: string, countries: Array<{ __typename?: 'Country', flag: string, code: string }> };

export const SidebarMenu_WorkspaceFragmentDoc = gql`
    fragment SidebarMenu_workspace on Workspace {
  slug
  name
  countries {
    flag
    code
  }
}
    `;
export const SidebarMenuDocument = gql`
    query SidebarMenu($page: Int, $perPage: Int) {
  pendingWorkspaceInvitations(page: 1, perPage: 1) {
    totalItems
  }
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
 * __useSidebarMenuQuery__
 *
 * To run a query within a React component, call `useSidebarMenuQuery` and pass it any options that fit your needs.
 * When your component renders, `useSidebarMenuQuery` returns an object from Apollo Client that contains loading, error, and data properties
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = useSidebarMenuQuery({
 *   variables: {
 *      page: // value for 'page'
 *      perPage: // value for 'perPage'
 *   },
 * });
 */
export function useSidebarMenuQuery(baseOptions?: Apollo.QueryHookOptions<SidebarMenuQuery, SidebarMenuQueryVariables>) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useQuery<SidebarMenuQuery, SidebarMenuQueryVariables>(SidebarMenuDocument, options);
      }
export function useSidebarMenuLazyQuery(baseOptions?: Apollo.LazyQueryHookOptions<SidebarMenuQuery, SidebarMenuQueryVariables>) {
          const options = {...defaultOptions, ...baseOptions}
          return Apollo.useLazyQuery<SidebarMenuQuery, SidebarMenuQueryVariables>(SidebarMenuDocument, options);
        }
export function useSidebarMenuSuspenseQuery(baseOptions?: Apollo.SkipToken | Apollo.SuspenseQueryHookOptions<SidebarMenuQuery, SidebarMenuQueryVariables>) {
          const options = baseOptions === Apollo.skipToken ? baseOptions : {...defaultOptions, ...baseOptions}
          return Apollo.useSuspenseQuery<SidebarMenuQuery, SidebarMenuQueryVariables>(SidebarMenuDocument, options);
        }
export type SidebarMenuQueryHookResult = ReturnType<typeof useSidebarMenuQuery>;
export type SidebarMenuLazyQueryHookResult = ReturnType<typeof useSidebarMenuLazyQuery>;
export type SidebarMenuSuspenseQueryHookResult = ReturnType<typeof useSidebarMenuSuspenseQuery>;
export type SidebarMenuQueryResult = Apollo.QueryResult<SidebarMenuQuery, SidebarMenuQueryVariables>;
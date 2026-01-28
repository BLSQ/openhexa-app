import * as Types from '../../../../graphql/types';

import { gql } from '@apollo/client';
import { WorkspaceLayout_WorkspaceFragmentDoc } from '../../../../workspaces/layouts/WorkspaceLayout/WorkspaceLayout.generated';
import * as Apollo from '@apollo/client';
const defaultOptions = {} as const;
export type WorkspaceAssistantPageQueryVariables = Types.Exact<{
  workspaceSlug: Types.Scalars['String']['input'];
}>;


export type WorkspaceAssistantPageQuery = { __typename?: 'Query', workspace?: { __typename?: 'Workspace', slug: string, name: string, assistantEnabled: boolean, permissions: { __typename?: 'WorkspacePermissions', update: boolean, manageMembers: boolean, launchNotebookServer: boolean }, shortcuts: Array<{ __typename?: 'ShortcutItem', id: string, name: string, url: string, order: number }>, countries: Array<{ __typename?: 'Country', flag: string, code: string }>, organization?: { __typename?: 'Organization', id: string, name: string, shortName?: string | null, logo?: string | null, permissions: { __typename?: 'OrganizationPermissions', createWorkspace: boolean } } | null } | null };


export const WorkspaceAssistantPageDocument = gql`
    query WorkspaceAssistantPage($workspaceSlug: String!) {
  workspace(slug: $workspaceSlug) {
    slug
    name
    assistantEnabled
    permissions {
      update
    }
    ...WorkspaceLayout_workspace
  }
}
    ${WorkspaceLayout_WorkspaceFragmentDoc}`;

/**
 * __useWorkspaceAssistantPageQuery__
 *
 * To run a query within a React component, call `useWorkspaceAssistantPageQuery` and pass it any options that fit your needs.
 * When your component renders, `useWorkspaceAssistantPageQuery` returns an object from Apollo Client that contains loading, error, and data properties
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = useWorkspaceAssistantPageQuery({
 *   variables: {
 *      workspaceSlug: // value for 'workspaceSlug'
 *   },
 * });
 */
export function useWorkspaceAssistantPageQuery(baseOptions: Apollo.QueryHookOptions<WorkspaceAssistantPageQuery, WorkspaceAssistantPageQueryVariables> & ({ variables: WorkspaceAssistantPageQueryVariables; skip?: boolean; } | { skip: boolean; }) ) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useQuery<WorkspaceAssistantPageQuery, WorkspaceAssistantPageQueryVariables>(WorkspaceAssistantPageDocument, options);
      }
export function useWorkspaceAssistantPageLazyQuery(baseOptions?: Apollo.LazyQueryHookOptions<WorkspaceAssistantPageQuery, WorkspaceAssistantPageQueryVariables>) {
          const options = {...defaultOptions, ...baseOptions}
          return Apollo.useLazyQuery<WorkspaceAssistantPageQuery, WorkspaceAssistantPageQueryVariables>(WorkspaceAssistantPageDocument, options);
        }
export function useWorkspaceAssistantPageSuspenseQuery(baseOptions?: Apollo.SkipToken | Apollo.SuspenseQueryHookOptions<WorkspaceAssistantPageQuery, WorkspaceAssistantPageQueryVariables>) {
          const options = baseOptions === Apollo.skipToken ? baseOptions : {...defaultOptions, ...baseOptions}
          return Apollo.useSuspenseQuery<WorkspaceAssistantPageQuery, WorkspaceAssistantPageQueryVariables>(WorkspaceAssistantPageDocument, options);
        }
export type WorkspaceAssistantPageQueryHookResult = ReturnType<typeof useWorkspaceAssistantPageQuery>;
export type WorkspaceAssistantPageLazyQueryHookResult = ReturnType<typeof useWorkspaceAssistantPageLazyQuery>;
export type WorkspaceAssistantPageSuspenseQueryHookResult = ReturnType<typeof useWorkspaceAssistantPageSuspenseQuery>;
export type WorkspaceAssistantPageQueryResult = Apollo.QueryResult<WorkspaceAssistantPageQuery, WorkspaceAssistantPageQueryVariables>;
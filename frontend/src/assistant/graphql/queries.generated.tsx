import * as Types from '../../graphql/types';

import { gql } from '@apollo/client';
import { WorkspaceLayout_WorkspaceFragmentDoc } from '../../workspaces/layouts/WorkspaceLayout/WorkspaceLayout.generated';
import * as Apollo from '@apollo/client';
const defaultOptions = {} as const;
export type AssistantPageQueryVariables = Types.Exact<{
  workspaceSlug: Types.Scalars['String']['input'];
}>;


export type AssistantPageQuery = { __typename?: 'Query', workspace?: { __typename?: 'Workspace', slug: string, name: string, assistantConversations: Array<{ __typename?: 'AssistantConversation', id: string, createdAt: any, model: string }>, permissions: { __typename?: 'WorkspacePermissions', manageMembers: boolean, update: boolean, launchNotebookServer: boolean }, shortcuts: Array<{ __typename?: 'ShortcutItem', id: string, name: string, url: string, order: number }>, countries: Array<{ __typename?: 'Country', flag: string, code: string }>, organization?: { __typename?: 'Organization', id: string, name: string, shortName?: string | null, logo?: string | null, permissions: { __typename?: 'OrganizationPermissions', createWorkspace: boolean } } | null } | null };

export type AssistantConversationMessagesQueryVariables = Types.Exact<{
  id: Types.Scalars['UUID']['input'];
}>;


export type AssistantConversationMessagesQuery = { __typename?: 'Query', assistantConversation?: { __typename?: 'AssistantConversation', id: string, messages: Array<{ __typename?: 'AssistantMessage', id: string, role: string, content: string, createdAt: any }> } | null };


export const AssistantPageDocument = gql`
    query AssistantPage($workspaceSlug: String!) {
  workspace(slug: $workspaceSlug) {
    slug
    ...WorkspaceLayout_workspace
    assistantConversations {
      id
      createdAt
      model
    }
  }
}
    ${WorkspaceLayout_WorkspaceFragmentDoc}`;

/**
 * __useAssistantPageQuery__
 *
 * To run a query within a React component, call `useAssistantPageQuery` and pass it any options that fit your needs.
 * When your component renders, `useAssistantPageQuery` returns an object from Apollo Client that contains loading, error, and data properties
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = useAssistantPageQuery({
 *   variables: {
 *      workspaceSlug: // value for 'workspaceSlug'
 *   },
 * });
 */
export function useAssistantPageQuery(baseOptions: Apollo.QueryHookOptions<AssistantPageQuery, AssistantPageQueryVariables> & ({ variables: AssistantPageQueryVariables; skip?: boolean; } | { skip: boolean; }) ) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useQuery<AssistantPageQuery, AssistantPageQueryVariables>(AssistantPageDocument, options);
      }
export function useAssistantPageLazyQuery(baseOptions?: Apollo.LazyQueryHookOptions<AssistantPageQuery, AssistantPageQueryVariables>) {
          const options = {...defaultOptions, ...baseOptions}
          return Apollo.useLazyQuery<AssistantPageQuery, AssistantPageQueryVariables>(AssistantPageDocument, options);
        }
export function useAssistantPageSuspenseQuery(baseOptions?: Apollo.SkipToken | Apollo.SuspenseQueryHookOptions<AssistantPageQuery, AssistantPageQueryVariables>) {
          const options = baseOptions === Apollo.skipToken ? baseOptions : {...defaultOptions, ...baseOptions}
          return Apollo.useSuspenseQuery<AssistantPageQuery, AssistantPageQueryVariables>(AssistantPageDocument, options);
        }
export type AssistantPageQueryHookResult = ReturnType<typeof useAssistantPageQuery>;
export type AssistantPageLazyQueryHookResult = ReturnType<typeof useAssistantPageLazyQuery>;
export type AssistantPageSuspenseQueryHookResult = ReturnType<typeof useAssistantPageSuspenseQuery>;
export type AssistantPageQueryResult = Apollo.QueryResult<AssistantPageQuery, AssistantPageQueryVariables>;
export const AssistantConversationMessagesDocument = gql`
    query AssistantConversationMessages($id: UUID!) {
  assistantConversation(id: $id) {
    id
    messages {
      id
      role
      content
      createdAt
    }
  }
}
    `;

/**
 * __useAssistantConversationMessagesQuery__
 *
 * To run a query within a React component, call `useAssistantConversationMessagesQuery` and pass it any options that fit your needs.
 * When your component renders, `useAssistantConversationMessagesQuery` returns an object from Apollo Client that contains loading, error, and data properties
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = useAssistantConversationMessagesQuery({
 *   variables: {
 *      id: // value for 'id'
 *   },
 * });
 */
export function useAssistantConversationMessagesQuery(baseOptions: Apollo.QueryHookOptions<AssistantConversationMessagesQuery, AssistantConversationMessagesQueryVariables> & ({ variables: AssistantConversationMessagesQueryVariables; skip?: boolean; } | { skip: boolean; }) ) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useQuery<AssistantConversationMessagesQuery, AssistantConversationMessagesQueryVariables>(AssistantConversationMessagesDocument, options);
      }
export function useAssistantConversationMessagesLazyQuery(baseOptions?: Apollo.LazyQueryHookOptions<AssistantConversationMessagesQuery, AssistantConversationMessagesQueryVariables>) {
          const options = {...defaultOptions, ...baseOptions}
          return Apollo.useLazyQuery<AssistantConversationMessagesQuery, AssistantConversationMessagesQueryVariables>(AssistantConversationMessagesDocument, options);
        }
export function useAssistantConversationMessagesSuspenseQuery(baseOptions?: Apollo.SkipToken | Apollo.SuspenseQueryHookOptions<AssistantConversationMessagesQuery, AssistantConversationMessagesQueryVariables>) {
          const options = baseOptions === Apollo.skipToken ? baseOptions : {...defaultOptions, ...baseOptions}
          return Apollo.useSuspenseQuery<AssistantConversationMessagesQuery, AssistantConversationMessagesQueryVariables>(AssistantConversationMessagesDocument, options);
        }
export type AssistantConversationMessagesQueryHookResult = ReturnType<typeof useAssistantConversationMessagesQuery>;
export type AssistantConversationMessagesLazyQueryHookResult = ReturnType<typeof useAssistantConversationMessagesLazyQuery>;
export type AssistantConversationMessagesSuspenseQueryHookResult = ReturnType<typeof useAssistantConversationMessagesSuspenseQuery>;
export type AssistantConversationMessagesQueryResult = Apollo.QueryResult<AssistantConversationMessagesQuery, AssistantConversationMessagesQueryVariables>;
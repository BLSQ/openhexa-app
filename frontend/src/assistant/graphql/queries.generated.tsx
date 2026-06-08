import * as Types from '../../graphql/types';

import { gql } from '@apollo/client';
import * as Apollo from '@apollo/client';
const defaultOptions = {} as const;
export type AssistantConversationMessagesQueryVariables = Types.Exact<{
  id: Types.Scalars['UUID']['input'];
  page?: Types.InputMaybe<Types.Scalars['Int']['input']>;
  perPage?: Types.InputMaybe<Types.Scalars['Int']['input']>;
}>;


export type AssistantConversationMessagesQuery = { __typename?: 'Query', assistantConversation?: { __typename?: 'AssistantConversation', id: string, name?: string | null, messages: { __typename?: 'AssistantMessagePage', totalItems: number, totalPages: number, items: Array<{ __typename?: 'AssistantMessage', id: string, role: string, content: string, createdAt: any, toolInvocations: Array<{ __typename?: 'AssistantToolInvocation', id: string, createdAt: any, toolName: string, toolInput: any, toolOutput?: any | null, success: boolean }> }> } } | null };


export const AssistantConversationMessagesDocument = gql`
    query AssistantConversationMessages($id: UUID!, $page: Int = 1, $perPage: Int = 20) {
  assistantConversation(id: $id) {
    id
    name
    messages(page: $page, perPage: $perPage) {
      items {
        id
        role
        content
        createdAt
        toolInvocations {
          id
          createdAt
          toolName
          toolInput
          toolOutput
          success
        }
      }
      totalItems
      totalPages
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
 *      page: // value for 'page'
 *      perPage: // value for 'perPage'
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
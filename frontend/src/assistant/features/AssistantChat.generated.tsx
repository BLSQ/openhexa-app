import * as Types from '../../graphql/types';

import { gql } from '@apollo/client';
import * as Apollo from '@apollo/client';
const defaultOptions = {} as const;
export type SendAssistantMessageMutationVariables = Types.Exact<{
  input: Types.SendAssistantMessageInput;
}>;


export type SendAssistantMessageMutation = { __typename?: 'Mutation', sendAssistantMessage: { __typename?: 'SendAssistantMessageResult', success: boolean, status: Types.SendAssistantMessageStatus, errors: Array<Types.SendAssistantMessageError>, message?: { __typename?: 'AssistantMessage', id: string, role: string, content: string, createdAt: any } | null, usage?: { __typename?: 'AssistantUsage', inputTokens: number, outputTokens: number, cost: number } | null, pendingToolCall?: { __typename?: 'PendingToolCall', id: string, toolName: string, toolInput: any } | null } };

export type ApproveToolExecutionMutationVariables = Types.Exact<{
  input: Types.ApproveToolExecutionInput;
}>;


export type ApproveToolExecutionMutation = { __typename?: 'Mutation', approveToolExecution: { __typename?: 'ApproveToolExecutionResult', success: boolean, status: Types.SendAssistantMessageStatus, errors: Array<Types.ApproveToolExecutionError>, message?: { __typename?: 'AssistantMessage', id: string, role: string, content: string, createdAt: any } | null, usage?: { __typename?: 'AssistantUsage', inputTokens: number, outputTokens: number, cost: number } | null, pendingToolCall?: { __typename?: 'PendingToolCall', id: string, toolName: string, toolInput: any } | null } };

export type WorkspaceAssistantConversationsQueryVariables = Types.Exact<{
  workspaceSlug: Types.Scalars['String']['input'];
}>;


export type WorkspaceAssistantConversationsQuery = { __typename?: 'Query', workspace?: { __typename?: 'Workspace', slug: string, assistantConversations: Array<{ __typename?: 'AssistantConversation', id: string, createdAt: any, updatedAt: any, estimatedCost: number, messages: Array<{ __typename?: 'AssistantMessage', id: string, role: string, content: string, createdAt: any, toolName?: string | null }> }> } | null };

export type DeleteAssistantConversationMutationVariables = Types.Exact<{
  input: Types.DeleteAssistantConversationInput;
}>;


export type DeleteAssistantConversationMutation = { __typename?: 'Mutation', deleteAssistantConversation: { __typename?: 'DeleteAssistantConversationResult', success: boolean, errors: Array<Types.DeleteAssistantConversationError> } };


export const SendAssistantMessageDocument = gql`
    mutation SendAssistantMessage($input: SendAssistantMessageInput!) {
  sendAssistantMessage(input: $input) {
    success
    status
    errors
    message {
      id
      role
      content
      createdAt
    }
    usage {
      inputTokens
      outputTokens
      cost
    }
    pendingToolCall {
      id
      toolName
      toolInput
    }
  }
}
    `;
export type SendAssistantMessageMutationFn = Apollo.MutationFunction<SendAssistantMessageMutation, SendAssistantMessageMutationVariables>;

/**
 * __useSendAssistantMessageMutation__
 *
 * To run a mutation, you first call `useSendAssistantMessageMutation` within a React component and pass it any options that fit your needs.
 * When your component renders, `useSendAssistantMessageMutation` returns a tuple that includes:
 * - A mutate function that you can call at any time to execute the mutation
 * - An object with fields that represent the current status of the mutation's execution
 *
 * @param baseOptions options that will be passed into the mutation, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options-2;
 *
 * @example
 * const [sendAssistantMessageMutation, { data, loading, error }] = useSendAssistantMessageMutation({
 *   variables: {
 *      input: // value for 'input'
 *   },
 * });
 */
export function useSendAssistantMessageMutation(baseOptions?: Apollo.MutationHookOptions<SendAssistantMessageMutation, SendAssistantMessageMutationVariables>) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useMutation<SendAssistantMessageMutation, SendAssistantMessageMutationVariables>(SendAssistantMessageDocument, options);
      }
export type SendAssistantMessageMutationHookResult = ReturnType<typeof useSendAssistantMessageMutation>;
export type SendAssistantMessageMutationResult = Apollo.MutationResult<SendAssistantMessageMutation>;
export type SendAssistantMessageMutationOptions = Apollo.BaseMutationOptions<SendAssistantMessageMutation, SendAssistantMessageMutationVariables>;
export const ApproveToolExecutionDocument = gql`
    mutation ApproveToolExecution($input: ApproveToolExecutionInput!) {
  approveToolExecution(input: $input) {
    success
    status
    message {
      id
      role
      content
      createdAt
    }
    errors
    usage {
      inputTokens
      outputTokens
      cost
    }
    pendingToolCall {
      id
      toolName
      toolInput
    }
  }
}
    `;
export type ApproveToolExecutionMutationFn = Apollo.MutationFunction<ApproveToolExecutionMutation, ApproveToolExecutionMutationVariables>;

/**
 * __useApproveToolExecutionMutation__
 *
 * To run a mutation, you first call `useApproveToolExecutionMutation` within a React component and pass it any options that fit your needs.
 * When your component renders, `useApproveToolExecutionMutation` returns a tuple that includes:
 * - A mutate function that you can call at any time to execute the mutation
 * - An object with fields that represent the current status of the mutation's execution
 *
 * @param baseOptions options that will be passed into the mutation, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options-2;
 *
 * @example
 * const [approveToolExecutionMutation, { data, loading, error }] = useApproveToolExecutionMutation({
 *   variables: {
 *      input: // value for 'input'
 *   },
 * });
 */
export function useApproveToolExecutionMutation(baseOptions?: Apollo.MutationHookOptions<ApproveToolExecutionMutation, ApproveToolExecutionMutationVariables>) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useMutation<ApproveToolExecutionMutation, ApproveToolExecutionMutationVariables>(ApproveToolExecutionDocument, options);
      }
export type ApproveToolExecutionMutationHookResult = ReturnType<typeof useApproveToolExecutionMutation>;
export type ApproveToolExecutionMutationResult = Apollo.MutationResult<ApproveToolExecutionMutation>;
export type ApproveToolExecutionMutationOptions = Apollo.BaseMutationOptions<ApproveToolExecutionMutation, ApproveToolExecutionMutationVariables>;
export const WorkspaceAssistantConversationsDocument = gql`
    query WorkspaceAssistantConversations($workspaceSlug: String!) {
  workspace(slug: $workspaceSlug) {
    slug
    assistantConversations {
      id
      createdAt
      updatedAt
      messages {
        id
        role
        content
        createdAt
        toolName
      }
      estimatedCost
    }
  }
}
    `;

/**
 * __useWorkspaceAssistantConversationsQuery__
 *
 * To run a query within a React component, call `useWorkspaceAssistantConversationsQuery` and pass it any options that fit your needs.
 * When your component renders, `useWorkspaceAssistantConversationsQuery` returns an object from Apollo Client that contains loading, error, and data properties
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = useWorkspaceAssistantConversationsQuery({
 *   variables: {
 *      workspaceSlug: // value for 'workspaceSlug'
 *   },
 * });
 */
export function useWorkspaceAssistantConversationsQuery(baseOptions: Apollo.QueryHookOptions<WorkspaceAssistantConversationsQuery, WorkspaceAssistantConversationsQueryVariables> & ({ variables: WorkspaceAssistantConversationsQueryVariables; skip?: boolean; } | { skip: boolean; }) ) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useQuery<WorkspaceAssistantConversationsQuery, WorkspaceAssistantConversationsQueryVariables>(WorkspaceAssistantConversationsDocument, options);
      }
export function useWorkspaceAssistantConversationsLazyQuery(baseOptions?: Apollo.LazyQueryHookOptions<WorkspaceAssistantConversationsQuery, WorkspaceAssistantConversationsQueryVariables>) {
          const options = {...defaultOptions, ...baseOptions}
          return Apollo.useLazyQuery<WorkspaceAssistantConversationsQuery, WorkspaceAssistantConversationsQueryVariables>(WorkspaceAssistantConversationsDocument, options);
        }
export function useWorkspaceAssistantConversationsSuspenseQuery(baseOptions?: Apollo.SkipToken | Apollo.SuspenseQueryHookOptions<WorkspaceAssistantConversationsQuery, WorkspaceAssistantConversationsQueryVariables>) {
          const options = baseOptions === Apollo.skipToken ? baseOptions : {...defaultOptions, ...baseOptions}
          return Apollo.useSuspenseQuery<WorkspaceAssistantConversationsQuery, WorkspaceAssistantConversationsQueryVariables>(WorkspaceAssistantConversationsDocument, options);
        }
export type WorkspaceAssistantConversationsQueryHookResult = ReturnType<typeof useWorkspaceAssistantConversationsQuery>;
export type WorkspaceAssistantConversationsLazyQueryHookResult = ReturnType<typeof useWorkspaceAssistantConversationsLazyQuery>;
export type WorkspaceAssistantConversationsSuspenseQueryHookResult = ReturnType<typeof useWorkspaceAssistantConversationsSuspenseQuery>;
export type WorkspaceAssistantConversationsQueryResult = Apollo.QueryResult<WorkspaceAssistantConversationsQuery, WorkspaceAssistantConversationsQueryVariables>;
export const DeleteAssistantConversationDocument = gql`
    mutation DeleteAssistantConversation($input: DeleteAssistantConversationInput!) {
  deleteAssistantConversation(input: $input) {
    success
    errors
  }
}
    `;
export type DeleteAssistantConversationMutationFn = Apollo.MutationFunction<DeleteAssistantConversationMutation, DeleteAssistantConversationMutationVariables>;

/**
 * __useDeleteAssistantConversationMutation__
 *
 * To run a mutation, you first call `useDeleteAssistantConversationMutation` within a React component and pass it any options that fit your needs.
 * When your component renders, `useDeleteAssistantConversationMutation` returns a tuple that includes:
 * - A mutate function that you can call at any time to execute the mutation
 * - An object with fields that represent the current status of the mutation's execution
 *
 * @param baseOptions options that will be passed into the mutation, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options-2;
 *
 * @example
 * const [deleteAssistantConversationMutation, { data, loading, error }] = useDeleteAssistantConversationMutation({
 *   variables: {
 *      input: // value for 'input'
 *   },
 * });
 */
export function useDeleteAssistantConversationMutation(baseOptions?: Apollo.MutationHookOptions<DeleteAssistantConversationMutation, DeleteAssistantConversationMutationVariables>) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useMutation<DeleteAssistantConversationMutation, DeleteAssistantConversationMutationVariables>(DeleteAssistantConversationDocument, options);
      }
export type DeleteAssistantConversationMutationHookResult = ReturnType<typeof useDeleteAssistantConversationMutation>;
export type DeleteAssistantConversationMutationResult = Apollo.MutationResult<DeleteAssistantConversationMutation>;
export type DeleteAssistantConversationMutationOptions = Apollo.BaseMutationOptions<DeleteAssistantConversationMutation, DeleteAssistantConversationMutationVariables>;
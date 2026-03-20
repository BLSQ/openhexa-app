import * as Types from '../../../../graphql/types';

import { gql } from '@apollo/client';
import * as Apollo from '@apollo/client';
const defaultOptions = {} as const;
export type CreateConversationForPipelineMutationVariables = Types.Exact<{
  input: Types.CreateAssistantConversationInput;
}>;


export type CreateConversationForPipelineMutation = { __typename?: 'Mutation', createAssistantConversation: { __typename?: 'CreateAssistantConversationResult', success: boolean, errors: Array<Types.CreateAssistantConversationError>, conversation?: { __typename?: 'AssistantConversation', id: string } | null } };

export type SendMessageForPipelineMutationVariables = Types.Exact<{
  input: Types.SendAssistantMessageInput;
}>;


export type SendMessageForPipelineMutation = { __typename?: 'Mutation', sendAssistantMessage: { __typename?: 'SendAssistantMessageResult', success: boolean, errors: Array<string>, message?: { __typename?: 'AssistantMessage', id: string, content: string, toolInvocations: Array<{ __typename?: 'AssistantToolInvocation', toolName: string, toolOutput?: any | null, success: boolean }> } | null } };


export const CreateConversationForPipelineDocument = gql`
    mutation CreateConversationForPipeline($input: CreateAssistantConversationInput!) {
  createAssistantConversation(input: $input) {
    success
    errors
    conversation {
      id
    }
  }
}
    `;
export type CreateConversationForPipelineMutationFn = Apollo.MutationFunction<CreateConversationForPipelineMutation, CreateConversationForPipelineMutationVariables>;

/**
 * __useCreateConversationForPipelineMutation__
 *
 * To run a mutation, you first call `useCreateConversationForPipelineMutation` within a React component and pass it any options that fit your needs.
 * When your component renders, `useCreateConversationForPipelineMutation` returns a tuple that includes:
 * - A mutate function that you can call at any time to execute the mutation
 * - An object with fields that represent the current status of the mutation's execution
 *
 * @param baseOptions options that will be passed into the mutation, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options-2;
 *
 * @example
 * const [createConversationForPipelineMutation, { data, loading, error }] = useCreateConversationForPipelineMutation({
 *   variables: {
 *      input: // value for 'input'
 *   },
 * });
 */
export function useCreateConversationForPipelineMutation(baseOptions?: Apollo.MutationHookOptions<CreateConversationForPipelineMutation, CreateConversationForPipelineMutationVariables>) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useMutation<CreateConversationForPipelineMutation, CreateConversationForPipelineMutationVariables>(CreateConversationForPipelineDocument, options);
      }
export type CreateConversationForPipelineMutationHookResult = ReturnType<typeof useCreateConversationForPipelineMutation>;
export type CreateConversationForPipelineMutationResult = Apollo.MutationResult<CreateConversationForPipelineMutation>;
export type CreateConversationForPipelineMutationOptions = Apollo.BaseMutationOptions<CreateConversationForPipelineMutation, CreateConversationForPipelineMutationVariables>;
export const SendMessageForPipelineDocument = gql`
    mutation SendMessageForPipeline($input: SendAssistantMessageInput!) {
  sendAssistantMessage(input: $input) {
    success
    errors
    message {
      id
      content
      toolInvocations {
        toolName
        toolOutput
        success
      }
    }
  }
}
    `;
export type SendMessageForPipelineMutationFn = Apollo.MutationFunction<SendMessageForPipelineMutation, SendMessageForPipelineMutationVariables>;

/**
 * __useSendMessageForPipelineMutation__
 *
 * To run a mutation, you first call `useSendMessageForPipelineMutation` within a React component and pass it any options that fit your needs.
 * When your component renders, `useSendMessageForPipelineMutation` returns a tuple that includes:
 * - A mutate function that you can call at any time to execute the mutation
 * - An object with fields that represent the current status of the mutation's execution
 *
 * @param baseOptions options that will be passed into the mutation, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options-2;
 *
 * @example
 * const [sendMessageForPipelineMutation, { data, loading, error }] = useSendMessageForPipelineMutation({
 *   variables: {
 *      input: // value for 'input'
 *   },
 * });
 */
export function useSendMessageForPipelineMutation(baseOptions?: Apollo.MutationHookOptions<SendMessageForPipelineMutation, SendMessageForPipelineMutationVariables>) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useMutation<SendMessageForPipelineMutation, SendMessageForPipelineMutationVariables>(SendMessageForPipelineDocument, options);
      }
export type SendMessageForPipelineMutationHookResult = ReturnType<typeof useSendMessageForPipelineMutation>;
export type SendMessageForPipelineMutationResult = Apollo.MutationResult<SendMessageForPipelineMutation>;
export type SendMessageForPipelineMutationOptions = Apollo.BaseMutationOptions<SendMessageForPipelineMutation, SendMessageForPipelineMutationVariables>;
import * as Types from '../../graphql/types';

import { gql } from '@apollo/client';
import * as Apollo from '@apollo/client';
const defaultOptions = {} as const;
export type CreateAssistantConversationMutationVariables = Types.Exact<{
  input: Types.CreateAssistantConversationInput;
}>;


export type CreateAssistantConversationMutation = { __typename?: 'Mutation', createAssistantConversation?: { __typename?: 'AssistantConversation', id: string, createdAt: any, model: string } | null };

export type SendAssistantMessageMutationVariables = Types.Exact<{
  input: Types.SendAssistantMessageInput;
}>;


export type SendAssistantMessageMutation = { __typename?: 'Mutation', sendAssistantMessage: { __typename?: 'SendAssistantMessageResult', success: boolean, errors: Array<string>, message?: { __typename?: 'AssistantMessage', id: string, role: string, content: string, createdAt: any } | null } };


export const CreateAssistantConversationDocument = gql`
    mutation createAssistantConversation($input: CreateAssistantConversationInput!) {
  createAssistantConversation(input: $input) {
    id
    createdAt
    model
  }
}
    `;
export type CreateAssistantConversationMutationFn = Apollo.MutationFunction<CreateAssistantConversationMutation, CreateAssistantConversationMutationVariables>;

/**
 * __useCreateAssistantConversationMutation__
 *
 * To run a mutation, you first call `useCreateAssistantConversationMutation` within a React component and pass it any options that fit your needs.
 * When your component renders, `useCreateAssistantConversationMutation` returns a tuple that includes:
 * - A mutate function that you can call at any time to execute the mutation
 * - An object with fields that represent the current status of the mutation's execution
 *
 * @param baseOptions options that will be passed into the mutation, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options-2;
 *
 * @example
 * const [createAssistantConversationMutation, { data, loading, error }] = useCreateAssistantConversationMutation({
 *   variables: {
 *      input: // value for 'input'
 *   },
 * });
 */
export function useCreateAssistantConversationMutation(baseOptions?: Apollo.MutationHookOptions<CreateAssistantConversationMutation, CreateAssistantConversationMutationVariables>) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useMutation<CreateAssistantConversationMutation, CreateAssistantConversationMutationVariables>(CreateAssistantConversationDocument, options);
      }
export type CreateAssistantConversationMutationHookResult = ReturnType<typeof useCreateAssistantConversationMutation>;
export type CreateAssistantConversationMutationResult = Apollo.MutationResult<CreateAssistantConversationMutation>;
export type CreateAssistantConversationMutationOptions = Apollo.BaseMutationOptions<CreateAssistantConversationMutation, CreateAssistantConversationMutationVariables>;
export const SendAssistantMessageDocument = gql`
    mutation sendAssistantMessage($input: SendAssistantMessageInput!) {
  sendAssistantMessage(input: $input) {
    success
    errors
    message {
      id
      role
      content
      createdAt
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
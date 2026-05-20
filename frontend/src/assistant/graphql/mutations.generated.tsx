import * as Types from '../../graphql/types';

import { gql } from '@apollo/client';
import * as Apollo from '@apollo/client';
const defaultOptions = {} as const;
export type CreateAssistantConversationMutationVariables = Types.Exact<{
  input: Types.CreateAssistantConversationInput;
}>;


export type CreateAssistantConversationMutation = { __typename?: 'Mutation', createAssistantConversation: { __typename?: 'CreateAssistantConversationResult', success: boolean, errors: Array<Types.CreateAssistantConversationError>, conversation?: { __typename?: 'AssistantConversation', id: string, createdAt: any, updatedAt: any } | null } };

export type ResolveAssistantProposalMutationVariables = Types.Exact<{
  toolInvocationId: Types.Scalars['UUID']['input'];
}>;


export type ResolveAssistantProposalMutation = { __typename?: 'Mutation', resolveAssistantProposal: { __typename?: 'ResolveAssistantProposalResult', success: boolean, errors: Array<Types.ResolveAssistantProposalError> } };


export const CreateAssistantConversationDocument = gql`
    mutation createAssistantConversation($input: CreateAssistantConversationInput!) {
  createAssistantConversation(input: $input) {
    success
    errors
    conversation {
      id
      createdAt
      updatedAt
    }
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
export const ResolveAssistantProposalDocument = gql`
    mutation resolveAssistantProposal($toolInvocationId: UUID!) {
  resolveAssistantProposal(toolInvocationId: $toolInvocationId) {
    success
    errors
  }
}
    `;
export type ResolveAssistantProposalMutationFn = Apollo.MutationFunction<ResolveAssistantProposalMutation, ResolveAssistantProposalMutationVariables>;

/**
 * __useResolveAssistantProposalMutation__
 *
 * To run a mutation, you first call `useResolveAssistantProposalMutation` within a React component and pass it any options that fit your needs.
 * When your component renders, `useResolveAssistantProposalMutation` returns a tuple that includes:
 * - A mutate function that you can call at any time to execute the mutation
 * - An object with fields that represent the current status of the mutation's execution
 *
 * @param baseOptions options that will be passed into the mutation, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options-2;
 *
 * @example
 * const [resolveAssistantProposalMutation, { data, loading, error }] = useResolveAssistantProposalMutation({
 *   variables: {
 *      toolInvocationId: // value for 'toolInvocationId'
 *   },
 * });
 */
export function useResolveAssistantProposalMutation(baseOptions?: Apollo.MutationHookOptions<ResolveAssistantProposalMutation, ResolveAssistantProposalMutationVariables>) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useMutation<ResolveAssistantProposalMutation, ResolveAssistantProposalMutationVariables>(ResolveAssistantProposalDocument, options);
      }
export type ResolveAssistantProposalMutationHookResult = ReturnType<typeof useResolveAssistantProposalMutation>;
export type ResolveAssistantProposalMutationResult = Apollo.MutationResult<ResolveAssistantProposalMutation>;
export type ResolveAssistantProposalMutationOptions = Apollo.BaseMutationOptions<ResolveAssistantProposalMutation, ResolveAssistantProposalMutationVariables>;
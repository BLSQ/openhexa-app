import * as Types from '../../../graphql/types';

import { gql } from '@apollo/client';
import * as Apollo from '@apollo/client';
const defaultOptions = {} as const;
export type GenerateWebhookPipelineWebhookUrlMutationVariables = Types.Exact<{
  input: Types.GeneratePipelineWebhookUrlInput;
}>;


export type GenerateWebhookPipelineWebhookUrlMutation = { __typename?: 'Mutation', generatePipelineWebhookUrl: { __typename?: 'GeneratePipelineWebhookUrlResult', success: boolean, errors: Array<Types.GeneratePipelineWebhookUrlError>, pipeline?: { __typename?: 'Pipeline', id: string, code: string, webhookUrl?: string | null } | null } };

export type GeneratePipelineWebhookUrlDialog_PipelineFragment = { __typename?: 'Pipeline', id: string, code: string };

export const GeneratePipelineWebhookUrlDialog_PipelineFragmentDoc = gql`
    fragment GeneratePipelineWebhookUrlDialog_pipeline on Pipeline {
  id
  code
}
    `;
export const GenerateWebhookPipelineWebhookUrlDocument = gql`
    mutation generateWebhookPipelineWebhookUrl($input: GeneratePipelineWebhookUrlInput!) {
  generatePipelineWebhookUrl(input: $input) {
    success
    errors
    pipeline {
      id
      code
      webhookUrl
    }
  }
}
    `;
export type GenerateWebhookPipelineWebhookUrlMutationFn = Apollo.MutationFunction<GenerateWebhookPipelineWebhookUrlMutation, GenerateWebhookPipelineWebhookUrlMutationVariables>;

/**
 * __useGenerateWebhookPipelineWebhookUrlMutation__
 *
 * To run a mutation, you first call `useGenerateWebhookPipelineWebhookUrlMutation` within a React component and pass it any options that fit your needs.
 * When your component renders, `useGenerateWebhookPipelineWebhookUrlMutation` returns a tuple that includes:
 * - A mutate function that you can call at any time to execute the mutation
 * - An object with fields that represent the current status of the mutation's execution
 *
 * @param baseOptions options that will be passed into the mutation, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options-2;
 *
 * @example
 * const [generateWebhookPipelineWebhookUrlMutation, { data, loading, error }] = useGenerateWebhookPipelineWebhookUrlMutation({
 *   variables: {
 *      input: // value for 'input'
 *   },
 * });
 */
export function useGenerateWebhookPipelineWebhookUrlMutation(baseOptions?: Apollo.MutationHookOptions<GenerateWebhookPipelineWebhookUrlMutation, GenerateWebhookPipelineWebhookUrlMutationVariables>) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useMutation<GenerateWebhookPipelineWebhookUrlMutation, GenerateWebhookPipelineWebhookUrlMutationVariables>(GenerateWebhookPipelineWebhookUrlDocument, options);
      }
export type GenerateWebhookPipelineWebhookUrlMutationHookResult = ReturnType<typeof useGenerateWebhookPipelineWebhookUrlMutation>;
export type GenerateWebhookPipelineWebhookUrlMutationResult = Apollo.MutationResult<GenerateWebhookPipelineWebhookUrlMutation>;
export type GenerateWebhookPipelineWebhookUrlMutationOptions = Apollo.BaseMutationOptions<GenerateWebhookPipelineWebhookUrlMutation, GenerateWebhookPipelineWebhookUrlMutationVariables>;
import * as Types from '../../../graphql/types';

import { gql } from '@apollo/client';
import { BucketObjectPicker_WorkspaceFragmentDoc } from '../BucketObjectPicker/BucketObjectPicker.generated';
import * as Apollo from '@apollo/client';
const defaultOptions = {} as const;
export type GenerateWorkspaceTokenMutationVariables = Types.Exact<{
  input: Types.GenerateWorkspaceTokenInput;
}>;


export type GenerateWorkspaceTokenMutation = { __typename?: 'Mutation', generateWorkspaceToken: { __typename?: 'GenerateWorkspaceTokenResult', token?: string | null, success: boolean } };

export type CreatePipelineDialog_WorkspaceFragment = { __typename?: 'Workspace', slug: string };

export const CreatePipelineDialog_WorkspaceFragmentDoc = gql`
    fragment CreatePipelineDialog_workspace on Workspace {
  slug
  ...BucketObjectPicker_workspace
}
    ${BucketObjectPicker_WorkspaceFragmentDoc}`;
export const GenerateWorkspaceTokenDocument = gql`
    mutation GenerateWorkspaceToken($input: GenerateWorkspaceTokenInput!) {
  generateWorkspaceToken(input: $input) {
    token
    success
  }
}
    `;
export type GenerateWorkspaceTokenMutationFn = Apollo.MutationFunction<GenerateWorkspaceTokenMutation, GenerateWorkspaceTokenMutationVariables>;

/**
 * __useGenerateWorkspaceTokenMutation__
 *
 * To run a mutation, you first call `useGenerateWorkspaceTokenMutation` within a React component and pass it any options that fit your needs.
 * When your component renders, `useGenerateWorkspaceTokenMutation` returns a tuple that includes:
 * - A mutate function that you can call at any time to execute the mutation
 * - An object with fields that represent the current status of the mutation's execution
 *
 * @param baseOptions options that will be passed into the mutation, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options-2;
 *
 * @example
 * const [generateWorkspaceTokenMutation, { data, loading, error }] = useGenerateWorkspaceTokenMutation({
 *   variables: {
 *      input: // value for 'input'
 *   },
 * });
 */
export function useGenerateWorkspaceTokenMutation(baseOptions?: Apollo.MutationHookOptions<GenerateWorkspaceTokenMutation, GenerateWorkspaceTokenMutationVariables>) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useMutation<GenerateWorkspaceTokenMutation, GenerateWorkspaceTokenMutationVariables>(GenerateWorkspaceTokenDocument, options);
      }
export type GenerateWorkspaceTokenMutationHookResult = ReturnType<typeof useGenerateWorkspaceTokenMutation>;
export type GenerateWorkspaceTokenMutationResult = Apollo.MutationResult<GenerateWorkspaceTokenMutation>;
export type GenerateWorkspaceTokenMutationOptions = Apollo.BaseMutationOptions<GenerateWorkspaceTokenMutation, GenerateWorkspaceTokenMutationVariables>;
import * as Types from '../../graphql/types';

import { gql } from '@apollo/client';
import * as Apollo from '@apollo/client';
const defaultOptions = {} as const;
export type LaunchNotebookServerMutationVariables = Types.Exact<{
  input: Types.LaunchNotebookServerInput;
}>;


export type LaunchNotebookServerMutation = { __typename?: 'Mutation', launchNotebookServer: { __typename?: 'LaunchNotebookServerResult', success: boolean, server?: { __typename?: 'NotebookServer', name: string, ready: boolean, url: string } | null } };


export const LaunchNotebookServerDocument = gql`
    mutation launchNotebookServer($input: LaunchNotebookServerInput!) {
  launchNotebookServer(input: $input) {
    success
    server {
      name
      ready
      url
    }
  }
}
    `;
export type LaunchNotebookServerMutationFn = Apollo.MutationFunction<LaunchNotebookServerMutation, LaunchNotebookServerMutationVariables>;

/**
 * __useLaunchNotebookServerMutation__
 *
 * To run a mutation, you first call `useLaunchNotebookServerMutation` within a React component and pass it any options that fit your needs.
 * When your component renders, `useLaunchNotebookServerMutation` returns a tuple that includes:
 * - A mutate function that you can call at any time to execute the mutation
 * - An object with fields that represent the current status of the mutation's execution
 *
 * @param baseOptions options that will be passed into the mutation, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options-2;
 *
 * @example
 * const [launchNotebookServerMutation, { data, loading, error }] = useLaunchNotebookServerMutation({
 *   variables: {
 *      input: // value for 'input'
 *   },
 * });
 */
export function useLaunchNotebookServerMutation(baseOptions?: Apollo.MutationHookOptions<LaunchNotebookServerMutation, LaunchNotebookServerMutationVariables>) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useMutation<LaunchNotebookServerMutation, LaunchNotebookServerMutationVariables>(LaunchNotebookServerDocument, options);
      }
export type LaunchNotebookServerMutationHookResult = ReturnType<typeof useLaunchNotebookServerMutation>;
export type LaunchNotebookServerMutationResult = Apollo.MutationResult<LaunchNotebookServerMutation>;
export type LaunchNotebookServerMutationOptions = Apollo.BaseMutationOptions<LaunchNotebookServerMutation, LaunchNotebookServerMutationVariables>;
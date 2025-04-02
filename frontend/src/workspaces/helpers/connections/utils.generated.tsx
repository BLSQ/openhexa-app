import * as Types from '../../../graphql/types';

import { gql } from '@apollo/client';
import * as Apollo from '@apollo/client';
const defaultOptions = {} as const;
export type DeleteConnectionMutationVariables = Types.Exact<{
  input: Types.DeleteConnectionInput;
}>;


export type DeleteConnectionMutation = { __typename?: 'Mutation', deleteConnection: { __typename?: 'DeleteConnectionResult', success: boolean, errors: Array<Types.DeleteConnectionError> } };


export const DeleteConnectionDocument = gql`
    mutation DeleteConnection($input: DeleteConnectionInput!) {
  deleteConnection(input: $input) {
    success
    errors
  }
}
    `;
export type DeleteConnectionMutationFn = Apollo.MutationFunction<DeleteConnectionMutation, DeleteConnectionMutationVariables>;

/**
 * __useDeleteConnectionMutation__
 *
 * To run a mutation, you first call `useDeleteConnectionMutation` within a React component and pass it any options that fit your needs.
 * When your component renders, `useDeleteConnectionMutation` returns a tuple that includes:
 * - A mutate function that you can call at any time to execute the mutation
 * - An object with fields that represent the current status of the mutation's execution
 *
 * @param baseOptions options that will be passed into the mutation, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options-2;
 *
 * @example
 * const [deleteConnectionMutation, { data, loading, error }] = useDeleteConnectionMutation({
 *   variables: {
 *      input: // value for 'input'
 *   },
 * });
 */
export function useDeleteConnectionMutation(baseOptions?: Apollo.MutationHookOptions<DeleteConnectionMutation, DeleteConnectionMutationVariables>) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useMutation<DeleteConnectionMutation, DeleteConnectionMutationVariables>(DeleteConnectionDocument, options);
      }
export type DeleteConnectionMutationHookResult = ReturnType<typeof useDeleteConnectionMutation>;
export type DeleteConnectionMutationResult = Apollo.MutationResult<DeleteConnectionMutation>;
export type DeleteConnectionMutationOptions = Apollo.BaseMutationOptions<DeleteConnectionMutation, DeleteConnectionMutationVariables>;
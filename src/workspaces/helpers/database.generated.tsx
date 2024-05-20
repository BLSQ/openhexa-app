import * as Types from '../../graphql/types';

import { gql } from '@apollo/client';
import * as Apollo from '@apollo/client';
const defaultOptions = {} as const;
export type DeleteWorkspaceDatabaseTableMutationVariables = Types.Exact<{
  input: Types.DeleteWorkspaceDatabaseTableInput;
}>;


export type DeleteWorkspaceDatabaseTableMutation = { __typename?: 'Mutation', deleteWorkspaceDatabaseTable?: { __typename?: 'DeleteWorkspaceDatabaseTableResult', success: boolean, errors: Array<Types.DeleteWorkspaceDatabaseTableError> } | null };


export const DeleteWorkspaceDatabaseTableDocument = gql`
    mutation deleteWorkspaceDatabaseTable($input: DeleteWorkspaceDatabaseTableInput!) {
  deleteWorkspaceDatabaseTable(input: $input) {
    success
    errors
  }
}
    `;
export type DeleteWorkspaceDatabaseTableMutationFn = Apollo.MutationFunction<DeleteWorkspaceDatabaseTableMutation, DeleteWorkspaceDatabaseTableMutationVariables>;

/**
 * __useDeleteWorkspaceDatabaseTableMutation__
 *
 * To run a mutation, you first call `useDeleteWorkspaceDatabaseTableMutation` within a React component and pass it any options that fit your needs.
 * When your component renders, `useDeleteWorkspaceDatabaseTableMutation` returns a tuple that includes:
 * - A mutate function that you can call at any time to execute the mutation
 * - An object with fields that represent the current status of the mutation's execution
 *
 * @param baseOptions options that will be passed into the mutation, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options-2;
 *
 * @example
 * const [deleteWorkspaceDatabaseTableMutation, { data, loading, error }] = useDeleteWorkspaceDatabaseTableMutation({
 *   variables: {
 *      input: // value for 'input'
 *   },
 * });
 */
export function useDeleteWorkspaceDatabaseTableMutation(baseOptions?: Apollo.MutationHookOptions<DeleteWorkspaceDatabaseTableMutation, DeleteWorkspaceDatabaseTableMutationVariables>) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useMutation<DeleteWorkspaceDatabaseTableMutation, DeleteWorkspaceDatabaseTableMutationVariables>(DeleteWorkspaceDatabaseTableDocument, options);
      }
export type DeleteWorkspaceDatabaseTableMutationHookResult = ReturnType<typeof useDeleteWorkspaceDatabaseTableMutation>;
export type DeleteWorkspaceDatabaseTableMutationResult = Apollo.MutationResult<DeleteWorkspaceDatabaseTableMutation>;
export type DeleteWorkspaceDatabaseTableMutationOptions = Apollo.BaseMutationOptions<DeleteWorkspaceDatabaseTableMutation, DeleteWorkspaceDatabaseTableMutationVariables>;
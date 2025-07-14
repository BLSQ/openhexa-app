import * as Types from '../../../../graphql/types';

import { gql } from '@apollo/client';
import * as Apollo from '@apollo/client';
const defaultOptions = {} as const;
export type DeleteOrganizationMemberMutationVariables = Types.Exact<{
  input: Types.DeleteOrganizationMemberInput;
}>;


export type DeleteOrganizationMemberMutation = { __typename?: 'Mutation', deleteOrganizationMember: { __typename?: 'DeleteOrganizationMemberResult', success: boolean, errors: Array<Types.DeleteOrganizationMemberError> } };


export const DeleteOrganizationMemberDocument = gql`
    mutation DeleteOrganizationMember($input: DeleteOrganizationMemberInput!) {
  deleteOrganizationMember(input: $input) {
    success
    errors
  }
}
    `;
export type DeleteOrganizationMemberMutationFn = Apollo.MutationFunction<DeleteOrganizationMemberMutation, DeleteOrganizationMemberMutationVariables>;

/**
 * __useDeleteOrganizationMemberMutation__
 *
 * To run a mutation, you first call `useDeleteOrganizationMemberMutation` within a React component and pass it any options that fit your needs.
 * When your component renders, `useDeleteOrganizationMemberMutation` returns a tuple that includes:
 * - A mutate function that you can call at any time to execute the mutation
 * - An object with fields that represent the current status of the mutation's execution
 *
 * @param baseOptions options that will be passed into the mutation, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options-2;
 *
 * @example
 * const [deleteOrganizationMemberMutation, { data, loading, error }] = useDeleteOrganizationMemberMutation({
 *   variables: {
 *      input: // value for 'input'
 *   },
 * });
 */
export function useDeleteOrganizationMemberMutation(baseOptions?: Apollo.MutationHookOptions<DeleteOrganizationMemberMutation, DeleteOrganizationMemberMutationVariables>) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useMutation<DeleteOrganizationMemberMutation, DeleteOrganizationMemberMutationVariables>(DeleteOrganizationMemberDocument, options);
      }
export type DeleteOrganizationMemberMutationHookResult = ReturnType<typeof useDeleteOrganizationMemberMutation>;
export type DeleteOrganizationMemberMutationResult = Apollo.MutationResult<DeleteOrganizationMemberMutation>;
export type DeleteOrganizationMemberMutationOptions = Apollo.BaseMutationOptions<DeleteOrganizationMemberMutation, DeleteOrganizationMemberMutationVariables>;
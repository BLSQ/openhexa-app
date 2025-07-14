import * as Types from '../../../../graphql/types';

import { gql } from '@apollo/client';
import * as Apollo from '@apollo/client';
const defaultOptions = {} as const;
export type AddOrganizationMemberMutationVariables = Types.Exact<{
  input: Types.AddOrganizationMemberInput;
}>;


export type AddOrganizationMemberMutation = { __typename?: 'Mutation', addOrganizationMember: { __typename?: 'AddOrganizationMemberResult', success: boolean, errors: Array<Types.AddOrganizationMemberError>, membership?: { __typename?: 'OrganizationMembership', id: string, role: Types.OrganizationMembershipRole, user: { __typename?: 'User', id: string, displayName: string, email: string } } | null } };


export const AddOrganizationMemberDocument = gql`
    mutation AddOrganizationMember($input: AddOrganizationMemberInput!) {
  addOrganizationMember(input: $input) {
    success
    errors
    membership {
      id
      user {
        id
        displayName
        email
      }
      role
    }
  }
}
    `;
export type AddOrganizationMemberMutationFn = Apollo.MutationFunction<AddOrganizationMemberMutation, AddOrganizationMemberMutationVariables>;

/**
 * __useAddOrganizationMemberMutation__
 *
 * To run a mutation, you first call `useAddOrganizationMemberMutation` within a React component and pass it any options that fit your needs.
 * When your component renders, `useAddOrganizationMemberMutation` returns a tuple that includes:
 * - A mutate function that you can call at any time to execute the mutation
 * - An object with fields that represent the current status of the mutation's execution
 *
 * @param baseOptions options that will be passed into the mutation, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options-2;
 *
 * @example
 * const [addOrganizationMemberMutation, { data, loading, error }] = useAddOrganizationMemberMutation({
 *   variables: {
 *      input: // value for 'input'
 *   },
 * });
 */
export function useAddOrganizationMemberMutation(baseOptions?: Apollo.MutationHookOptions<AddOrganizationMemberMutation, AddOrganizationMemberMutationVariables>) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useMutation<AddOrganizationMemberMutation, AddOrganizationMemberMutationVariables>(AddOrganizationMemberDocument, options);
      }
export type AddOrganizationMemberMutationHookResult = ReturnType<typeof useAddOrganizationMemberMutation>;
export type AddOrganizationMemberMutationResult = Apollo.MutationResult<AddOrganizationMemberMutation>;
export type AddOrganizationMemberMutationOptions = Apollo.BaseMutationOptions<AddOrganizationMemberMutation, AddOrganizationMemberMutationVariables>;
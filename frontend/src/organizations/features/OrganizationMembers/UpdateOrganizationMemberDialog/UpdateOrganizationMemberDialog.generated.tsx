import * as Types from '../../../../graphql/types';

import { gql } from '@apollo/client';
import * as Apollo from '@apollo/client';
const defaultOptions = {} as const;
export type UpdateOrganizationMemberMutationVariables = Types.Exact<{
  input: Types.UpdateOrganizationMemberInput;
}>;


export type UpdateOrganizationMemberMutation = { __typename?: 'Mutation', updateOrganizationMember: { __typename?: 'UpdateOrganizationMemberResult', success: boolean, errors: Array<Types.UpdateOrganizationMemberError>, membership?: { __typename?: 'OrganizationMembership', id: string, role: Types.OrganizationMembershipRole } | null } };


export const UpdateOrganizationMemberDocument = gql`
    mutation UpdateOrganizationMember($input: UpdateOrganizationMemberInput!) {
  updateOrganizationMember(input: $input) {
    success
    errors
    membership {
      id
      role
    }
  }
}
    `;
export type UpdateOrganizationMemberMutationFn = Apollo.MutationFunction<UpdateOrganizationMemberMutation, UpdateOrganizationMemberMutationVariables>;

/**
 * __useUpdateOrganizationMemberMutation__
 *
 * To run a mutation, you first call `useUpdateOrganizationMemberMutation` within a React component and pass it any options that fit your needs.
 * When your component renders, `useUpdateOrganizationMemberMutation` returns a tuple that includes:
 * - A mutate function that you can call at any time to execute the mutation
 * - An object with fields that represent the current status of the mutation's execution
 *
 * @param baseOptions options that will be passed into the mutation, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options-2;
 *
 * @example
 * const [updateOrganizationMemberMutation, { data, loading, error }] = useUpdateOrganizationMemberMutation({
 *   variables: {
 *      input: // value for 'input'
 *   },
 * });
 */
export function useUpdateOrganizationMemberMutation(baseOptions?: Apollo.MutationHookOptions<UpdateOrganizationMemberMutation, UpdateOrganizationMemberMutationVariables>) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useMutation<UpdateOrganizationMemberMutation, UpdateOrganizationMemberMutationVariables>(UpdateOrganizationMemberDocument, options);
      }
export type UpdateOrganizationMemberMutationHookResult = ReturnType<typeof useUpdateOrganizationMemberMutation>;
export type UpdateOrganizationMemberMutationResult = Apollo.MutationResult<UpdateOrganizationMemberMutation>;
export type UpdateOrganizationMemberMutationOptions = Apollo.BaseMutationOptions<UpdateOrganizationMemberMutation, UpdateOrganizationMemberMutationVariables>;
import * as Types from '../../../graphql/types';

import { gql } from '@apollo/client';
import * as Apollo from '@apollo/client';
const defaultOptions = {} as const;
export type UpdateOrganizationSettingsMutationVariables = Types.Exact<{
  input: Types.UpdateOrganizationSettingsInput;
}>;


export type UpdateOrganizationSettingsMutation = { __typename?: 'Mutation', updateOrganizationSettings: { __typename?: 'UpdateOrganizationSettingsResult', success: boolean, errors?: Array<Types.UpdateOrganizationSettingsError> | null, organization?: { __typename?: 'Organization', id: string, logo?: string | null, icon?: string | null } | null } };


export const UpdateOrganizationSettingsDocument = gql`
    mutation UpdateOrganizationSettings($input: UpdateOrganizationSettingsInput!) {
  updateOrganizationSettings(input: $input) {
    success
    errors
    organization {
      id
      logo
      icon
    }
  }
}
    `;
export type UpdateOrganizationSettingsMutationFn = Apollo.MutationFunction<UpdateOrganizationSettingsMutation, UpdateOrganizationSettingsMutationVariables>;

/**
 * __useUpdateOrganizationSettingsMutation__
 *
 * To run a mutation, you first call `useUpdateOrganizationSettingsMutation` within a React component and pass it any options that fit your needs.
 * When your component renders, `useUpdateOrganizationSettingsMutation` returns a tuple that includes:
 * - A mutate function that you can call at any time to execute the mutation
 * - An object with fields that represent the current status of the mutation's execution
 *
 * @param baseOptions options that will be passed into the mutation, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options-2;
 *
 * @example
 * const [updateOrganizationSettingsMutation, { data, loading, error }] = useUpdateOrganizationSettingsMutation({
 *   variables: {
 *      input: // value for 'input'
 *   },
 * });
 */
export function useUpdateOrganizationSettingsMutation(baseOptions?: Apollo.MutationHookOptions<UpdateOrganizationSettingsMutation, UpdateOrganizationSettingsMutationVariables>) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useMutation<UpdateOrganizationSettingsMutation, UpdateOrganizationSettingsMutationVariables>(UpdateOrganizationSettingsDocument, options);
      }
export type UpdateOrganizationSettingsMutationHookResult = ReturnType<typeof useUpdateOrganizationSettingsMutation>;
export type UpdateOrganizationSettingsMutationResult = Apollo.MutationResult<UpdateOrganizationSettingsMutation>;
export type UpdateOrganizationSettingsMutationOptions = Apollo.BaseMutationOptions<UpdateOrganizationSettingsMutation, UpdateOrganizationSettingsMutationVariables>;
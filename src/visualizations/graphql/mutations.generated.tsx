import * as Types from '../../graphql-types';

import { gql } from '@apollo/client';
import * as Apollo from '@apollo/client';
const defaultOptions = {} as const;
export type UpdateExternalDashboardMutationVariables = Types.Exact<{
  input: Types.UpdateExternalDashboardInput;
}>;


export type UpdateExternalDashboardMutation = { __typename?: 'Mutation', updateExternalDashboard: { __typename?: 'UpdateExternalDashboardResult', success: boolean, errors: Array<Types.UpdateExternalDashboardError>, externalDashboard?: { __typename?: 'ExternalDashboard', id: string, name: string, description?: string | null } | null } };


export const UpdateExternalDashboardDocument = gql`
    mutation updateExternalDashboard($input: UpdateExternalDashboardInput!) {
  updateExternalDashboard(input: $input) {
    success
    errors
    externalDashboard {
      id
      name
      description
    }
  }
}
    `;
export type UpdateExternalDashboardMutationFn = Apollo.MutationFunction<UpdateExternalDashboardMutation, UpdateExternalDashboardMutationVariables>;

/**
 * __useUpdateExternalDashboardMutation__
 *
 * To run a mutation, you first call `useUpdateExternalDashboardMutation` within a React component and pass it any options that fit your needs.
 * When your component renders, `useUpdateExternalDashboardMutation` returns a tuple that includes:
 * - A mutate function that you can call at any time to execute the mutation
 * - An object with fields that represent the current status of the mutation's execution
 *
 * @param baseOptions options that will be passed into the mutation, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options-2;
 *
 * @example
 * const [updateExternalDashboardMutation, { data, loading, error }] = useUpdateExternalDashboardMutation({
 *   variables: {
 *      input: // value for 'input'
 *   },
 * });
 */
export function useUpdateExternalDashboardMutation(baseOptions?: Apollo.MutationHookOptions<UpdateExternalDashboardMutation, UpdateExternalDashboardMutationVariables>) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useMutation<UpdateExternalDashboardMutation, UpdateExternalDashboardMutationVariables>(UpdateExternalDashboardDocument, options);
      }
export type UpdateExternalDashboardMutationHookResult = ReturnType<typeof useUpdateExternalDashboardMutation>;
export type UpdateExternalDashboardMutationResult = Apollo.MutationResult<UpdateExternalDashboardMutation>;
export type UpdateExternalDashboardMutationOptions = Apollo.BaseMutationOptions<UpdateExternalDashboardMutation, UpdateExternalDashboardMutationVariables>;
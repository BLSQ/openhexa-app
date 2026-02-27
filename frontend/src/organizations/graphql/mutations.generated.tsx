import * as Types from '../../graphql/types';

import { gql } from '@apollo/client';
import { Organization_OrganizationFragmentDoc } from './queries.generated';
import * as Apollo from '@apollo/client';
const defaultOptions = {} as const;
export type UpdateOrganizationMutationVariables = Types.Exact<{
  input: Types.UpdateOrganizationInput;
}>;


export type UpdateOrganizationMutation = { __typename?: 'Mutation', updateOrganization: { __typename?: 'UpdateOrganizationResult', success: boolean, errors: Array<Types.UpdateOrganizationError>, organization?: { __typename?: 'Organization', id: string, name: string, shortName?: string | null, logo?: string | null, workspaces: { __typename?: 'WorkspacePage', totalItems: number }, permissions: { __typename?: 'OrganizationPermissions', archiveWorkspace: boolean, manageMembers: boolean, manageOwners: boolean, update: boolean, delete: boolean, createWorkspace: { __typename?: 'CreateWorkspacePermission', isAllowed: boolean, reasons: Array<Types.CreateWorkspacePermissionReason> } }, members: { __typename?: 'OrganizationMembershipPage', totalItems: number }, externalCollaborators: { __typename?: 'ExternalCollaboratorPage', totalItems: number }, usage: { __typename?: 'ResourceCounts', users: number, workspaces: number, pipelineRuns: number }, subscription?: { __typename?: 'Subscription', subscriptionId: string, planCode: string, startDate: any, endDate: any, isExpired: boolean, isInGracePeriod: boolean, limits: { __typename?: 'ResourceCounts', users: number, workspaces: number, pipelineRuns: number } } | null } | null } };

export type DeleteOrganizationMutationVariables = Types.Exact<{
  input: Types.DeleteOrganizationInput;
}>;


export type DeleteOrganizationMutation = { __typename?: 'Mutation', deleteOrganization: { __typename?: 'DeleteOrganizationResult', success: boolean, errors: Array<Types.DeleteOrganizationError> } };


export const UpdateOrganizationDocument = gql`
    mutation UpdateOrganization($input: UpdateOrganizationInput!) {
  updateOrganization(input: $input) {
    success
    errors
    organization {
      ...Organization_organization
    }
  }
}
    ${Organization_OrganizationFragmentDoc}`;
export type UpdateOrganizationMutationFn = Apollo.MutationFunction<UpdateOrganizationMutation, UpdateOrganizationMutationVariables>;

/**
 * __useUpdateOrganizationMutation__
 *
 * To run a mutation, you first call `useUpdateOrganizationMutation` within a React component and pass it any options that fit your needs.
 * When your component renders, `useUpdateOrganizationMutation` returns a tuple that includes:
 * - A mutate function that you can call at any time to execute the mutation
 * - An object with fields that represent the current status of the mutation's execution
 *
 * @param baseOptions options that will be passed into the mutation, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options-2;
 *
 * @example
 * const [updateOrganizationMutation, { data, loading, error }] = useUpdateOrganizationMutation({
 *   variables: {
 *      input: // value for 'input'
 *   },
 * });
 */
export function useUpdateOrganizationMutation(baseOptions?: Apollo.MutationHookOptions<UpdateOrganizationMutation, UpdateOrganizationMutationVariables>) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useMutation<UpdateOrganizationMutation, UpdateOrganizationMutationVariables>(UpdateOrganizationDocument, options);
      }
export type UpdateOrganizationMutationHookResult = ReturnType<typeof useUpdateOrganizationMutation>;
export type UpdateOrganizationMutationResult = Apollo.MutationResult<UpdateOrganizationMutation>;
export type UpdateOrganizationMutationOptions = Apollo.BaseMutationOptions<UpdateOrganizationMutation, UpdateOrganizationMutationVariables>;
export const DeleteOrganizationDocument = gql`
    mutation DeleteOrganization($input: DeleteOrganizationInput!) {
  deleteOrganization(input: $input) {
    success
    errors
  }
}
    `;
export type DeleteOrganizationMutationFn = Apollo.MutationFunction<DeleteOrganizationMutation, DeleteOrganizationMutationVariables>;

/**
 * __useDeleteOrganizationMutation__
 *
 * To run a mutation, you first call `useDeleteOrganizationMutation` within a React component and pass it any options that fit your needs.
 * When your component renders, `useDeleteOrganizationMutation` returns a tuple that includes:
 * - A mutate function that you can call at any time to execute the mutation
 * - An object with fields that represent the current status of the mutation's execution
 *
 * @param baseOptions options that will be passed into the mutation, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options-2;
 *
 * @example
 * const [deleteOrganizationMutation, { data, loading, error }] = useDeleteOrganizationMutation({
 *   variables: {
 *      input: // value for 'input'
 *   },
 * });
 */
export function useDeleteOrganizationMutation(baseOptions?: Apollo.MutationHookOptions<DeleteOrganizationMutation, DeleteOrganizationMutationVariables>) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useMutation<DeleteOrganizationMutation, DeleteOrganizationMutationVariables>(DeleteOrganizationDocument, options);
      }
export type DeleteOrganizationMutationHookResult = ReturnType<typeof useDeleteOrganizationMutation>;
export type DeleteOrganizationMutationResult = Apollo.MutationResult<DeleteOrganizationMutation>;
export type DeleteOrganizationMutationOptions = Apollo.BaseMutationOptions<DeleteOrganizationMutation, DeleteOrganizationMutationVariables>;
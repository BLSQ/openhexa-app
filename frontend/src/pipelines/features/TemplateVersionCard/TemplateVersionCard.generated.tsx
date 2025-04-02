import * as Types from '../../../graphql/types';

import { gql } from '@apollo/client';
import { DeleteTemplateVersionTrigger_VersionFragmentDoc } from '../../../workspaces/features/DeleteTemplateVersionTrigger/DeleteTemplateVersionTrigger.generated';
import * as Apollo from '@apollo/client';
const defaultOptions = {} as const;
export type UpdateTemplateVersionMutationVariables = Types.Exact<{
  input: Types.UpdateTemplateVersionInput;
}>;


export type UpdateTemplateVersionMutation = { __typename?: 'Mutation', updateTemplateVersion: { __typename?: 'UpdateTemplateVersionResult', success: boolean, errors: Array<Types.UpdateTemplateVersionError>, templateVersion?: { __typename?: 'PipelineTemplateVersion', id: string, versionNumber: number, changelog?: string | null, createdAt: any, isLatestVersion: boolean, user?: { __typename?: 'User', displayName: string } | null, permissions: { __typename?: 'PipelineTemplateVersionPermissions', update: boolean, delete: boolean }, template: { __typename?: 'PipelineTemplate', id: string, code: string } } | null } };

export type TemplateVersionCard_VersionFragment = { __typename?: 'PipelineTemplateVersion', id: string, versionNumber: number, changelog?: string | null, createdAt: any, isLatestVersion: boolean, user?: { __typename?: 'User', displayName: string } | null, permissions: { __typename?: 'PipelineTemplateVersionPermissions', update: boolean, delete: boolean }, template: { __typename?: 'PipelineTemplate', id: string, code: string } };

export const TemplateVersionCard_VersionFragmentDoc = gql`
    fragment TemplateVersionCard_version on PipelineTemplateVersion {
  id
  versionNumber
  changelog
  createdAt
  isLatestVersion
  user {
    displayName
  }
  permissions {
    update
  }
  template {
    id
    code
  }
  ...DeleteTemplateVersionTrigger_version
}
    ${DeleteTemplateVersionTrigger_VersionFragmentDoc}`;
export const UpdateTemplateVersionDocument = gql`
    mutation UpdateTemplateVersion($input: UpdateTemplateVersionInput!) {
  updateTemplateVersion(input: $input) {
    success
    errors
    templateVersion {
      ...TemplateVersionCard_version
    }
  }
}
    ${TemplateVersionCard_VersionFragmentDoc}`;
export type UpdateTemplateVersionMutationFn = Apollo.MutationFunction<UpdateTemplateVersionMutation, UpdateTemplateVersionMutationVariables>;

/**
 * __useUpdateTemplateVersionMutation__
 *
 * To run a mutation, you first call `useUpdateTemplateVersionMutation` within a React component and pass it any options that fit your needs.
 * When your component renders, `useUpdateTemplateVersionMutation` returns a tuple that includes:
 * - A mutate function that you can call at any time to execute the mutation
 * - An object with fields that represent the current status of the mutation's execution
 *
 * @param baseOptions options that will be passed into the mutation, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options-2;
 *
 * @example
 * const [updateTemplateVersionMutation, { data, loading, error }] = useUpdateTemplateVersionMutation({
 *   variables: {
 *      input: // value for 'input'
 *   },
 * });
 */
export function useUpdateTemplateVersionMutation(baseOptions?: Apollo.MutationHookOptions<UpdateTemplateVersionMutation, UpdateTemplateVersionMutationVariables>) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useMutation<UpdateTemplateVersionMutation, UpdateTemplateVersionMutationVariables>(UpdateTemplateVersionDocument, options);
      }
export type UpdateTemplateVersionMutationHookResult = ReturnType<typeof useUpdateTemplateVersionMutation>;
export type UpdateTemplateVersionMutationResult = Apollo.MutationResult<UpdateTemplateVersionMutation>;
export type UpdateTemplateVersionMutationOptions = Apollo.BaseMutationOptions<UpdateTemplateVersionMutation, UpdateTemplateVersionMutationVariables>;
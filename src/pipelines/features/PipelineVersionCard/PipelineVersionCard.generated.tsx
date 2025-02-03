import * as Types from '../../../graphql/types';

import { gql } from '@apollo/client';
import { DownloadPipelineVersion_VersionFragmentDoc } from '../DownloadPipelineVersion/DownloadPipelineVersion.generated';
import { DeletePipelineVersionTrigger_VersionFragmentDoc } from '../../../workspaces/features/DeletePipelineVersionTrigger/DeletePipelineVersionTrigger.generated';
import * as Apollo from '@apollo/client';
const defaultOptions = {} as const;
export type UpdatePipelineVersionMutationVariables = Types.Exact<{
  input: Types.UpdatePipelineVersionInput;
}>;


export type UpdatePipelineVersionMutation = { __typename?: 'Mutation', updatePipelineVersion: { __typename?: 'UpdatePipelineVersionResult', success: boolean, errors: Array<Types.UpdatePipelineVersionError>, pipelineVersion?: { __typename?: 'PipelineVersion', id: string, versionName: string, name?: string | null, description?: string | null, externalLink?: any | null, isLatestVersion: boolean, createdAt: any, user?: { __typename?: 'User', displayName: string } | null, permissions: { __typename?: 'PipelineVersionPermissions', update: boolean, delete: boolean }, parameters: Array<{ __typename?: 'PipelineParameter', code: string, name: string, type: Types.ParameterType, multiple: boolean, required: boolean, help?: string | null }>, pipeline: { __typename?: 'Pipeline', id: string, code: string }, templateVersion?: { __typename?: 'PipelineTemplateVersion', id: string, versionNumber: number, template: { __typename?: 'PipelineTemplate', id: string, name: string } } | null } | null } };

export type PipelineVersionCard_VersionFragment = { __typename?: 'PipelineVersion', id: string, versionName: string, name?: string | null, description?: string | null, externalLink?: any | null, isLatestVersion: boolean, createdAt: any, user?: { __typename?: 'User', displayName: string } | null, permissions: { __typename?: 'PipelineVersionPermissions', update: boolean, delete: boolean }, parameters: Array<{ __typename?: 'PipelineParameter', code: string, name: string, type: Types.ParameterType, multiple: boolean, required: boolean, help?: string | null }>, pipeline: { __typename?: 'Pipeline', id: string, code: string }, templateVersion?: { __typename?: 'PipelineTemplateVersion', id: string, versionNumber: number, template: { __typename?: 'PipelineTemplate', id: string, name: string } } | null };

export const PipelineVersionCard_VersionFragmentDoc = gql`
    fragment PipelineVersionCard_version on PipelineVersion {
  id
  versionName
  name
  description
  externalLink
  isLatestVersion
  createdAt
  user {
    displayName
  }
  permissions {
    update
  }
  parameters {
    code
    name
    type
    multiple
    required
    help
  }
  pipeline {
    id
    code
  }
  templateVersion {
    id
    versionNumber
    template {
      id
      name
    }
  }
  ...DownloadPipelineVersion_version
  ...DeletePipelineVersionTrigger_version
}
    ${DownloadPipelineVersion_VersionFragmentDoc}
${DeletePipelineVersionTrigger_VersionFragmentDoc}`;
export const UpdatePipelineVersionDocument = gql`
    mutation UpdatePipelineVersion($input: UpdatePipelineVersionInput!) {
  updatePipelineVersion(input: $input) {
    success
    errors
    pipelineVersion {
      ...PipelineVersionCard_version
    }
  }
}
    ${PipelineVersionCard_VersionFragmentDoc}`;
export type UpdatePipelineVersionMutationFn = Apollo.MutationFunction<UpdatePipelineVersionMutation, UpdatePipelineVersionMutationVariables>;

/**
 * __useUpdatePipelineVersionMutation__
 *
 * To run a mutation, you first call `useUpdatePipelineVersionMutation` within a React component and pass it any options that fit your needs.
 * When your component renders, `useUpdatePipelineVersionMutation` returns a tuple that includes:
 * - A mutate function that you can call at any time to execute the mutation
 * - An object with fields that represent the current status of the mutation's execution
 *
 * @param baseOptions options that will be passed into the mutation, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options-2;
 *
 * @example
 * const [updatePipelineVersionMutation, { data, loading, error }] = useUpdatePipelineVersionMutation({
 *   variables: {
 *      input: // value for 'input'
 *   },
 * });
 */
export function useUpdatePipelineVersionMutation(baseOptions?: Apollo.MutationHookOptions<UpdatePipelineVersionMutation, UpdatePipelineVersionMutationVariables>) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useMutation<UpdatePipelineVersionMutation, UpdatePipelineVersionMutationVariables>(UpdatePipelineVersionDocument, options);
      }
export type UpdatePipelineVersionMutationHookResult = ReturnType<typeof useUpdatePipelineVersionMutation>;
export type UpdatePipelineVersionMutationResult = Apollo.MutationResult<UpdatePipelineVersionMutation>;
export type UpdatePipelineVersionMutationOptions = Apollo.BaseMutationOptions<UpdatePipelineVersionMutation, UpdatePipelineVersionMutationVariables>;
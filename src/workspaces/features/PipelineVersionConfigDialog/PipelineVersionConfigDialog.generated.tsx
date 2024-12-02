import * as Types from '../../../graphql/types';

import { gql } from '@apollo/client';
import { ParameterField_ParameterFragmentDoc } from '../RunPipelineDialog/ParameterField.generated';
import * as Apollo from '@apollo/client';
const defaultOptions = {} as const;
export type UpdatePipelineVersionConfigMutationVariables = Types.Exact<{
  input: Types.UpdatePipelineVersionInput;
}>;


export type UpdatePipelineVersionConfigMutation = { __typename?: 'Mutation', updatePipelineVersion: { __typename?: 'UpdatePipelineVersionResult', success: boolean, errors: Array<Types.UpdatePipelineVersionError>, pipelineVersion?: { __typename?: 'PipelineVersion', id: string, config?: any | null } | null } };

export type PipelineVersionConfigDialog_VersionFragment = { __typename?: 'PipelineVersion', id: string, name?: string | null, description?: string | null, externalLink?: any | null, isLatestVersion: boolean, createdAt: any, config?: any | null, pipeline: { __typename?: 'Pipeline', id: string, schedule?: string | null, workspace: { __typename?: 'Workspace', slug: string } }, parameters: Array<{ __typename?: 'PipelineParameter', code: string, name: string, help?: string | null, type: Types.ParameterType, default?: any | null, required: boolean, choices?: Array<any> | null, multiple: boolean }> };

export const PipelineVersionConfigDialog_VersionFragmentDoc = gql`
    fragment PipelineVersionConfigDialog_version on PipelineVersion {
  id
  name
  description
  externalLink
  isLatestVersion
  createdAt
  config
  pipeline {
    id
    schedule
    workspace {
      slug
    }
  }
  parameters {
    ...ParameterField_parameter
  }
}
    ${ParameterField_ParameterFragmentDoc}`;
export const UpdatePipelineVersionConfigDocument = gql`
    mutation UpdatePipelineVersionConfig($input: UpdatePipelineVersionInput!) {
  updatePipelineVersion(input: $input) {
    success
    errors
    pipelineVersion {
      id
      config
    }
  }
}
    `;
export type UpdatePipelineVersionConfigMutationFn = Apollo.MutationFunction<UpdatePipelineVersionConfigMutation, UpdatePipelineVersionConfigMutationVariables>;

/**
 * __useUpdatePipelineVersionConfigMutation__
 *
 * To run a mutation, you first call `useUpdatePipelineVersionConfigMutation` within a React component and pass it any options that fit your needs.
 * When your component renders, `useUpdatePipelineVersionConfigMutation` returns a tuple that includes:
 * - A mutate function that you can call at any time to execute the mutation
 * - An object with fields that represent the current status of the mutation's execution
 *
 * @param baseOptions options that will be passed into the mutation, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options-2;
 *
 * @example
 * const [updatePipelineVersionConfigMutation, { data, loading, error }] = useUpdatePipelineVersionConfigMutation({
 *   variables: {
 *      input: // value for 'input'
 *   },
 * });
 */
export function useUpdatePipelineVersionConfigMutation(baseOptions?: Apollo.MutationHookOptions<UpdatePipelineVersionConfigMutation, UpdatePipelineVersionConfigMutationVariables>) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useMutation<UpdatePipelineVersionConfigMutation, UpdatePipelineVersionConfigMutationVariables>(UpdatePipelineVersionConfigDocument, options);
      }
export type UpdatePipelineVersionConfigMutationHookResult = ReturnType<typeof useUpdatePipelineVersionConfigMutation>;
export type UpdatePipelineVersionConfigMutationResult = Apollo.MutationResult<UpdatePipelineVersionConfigMutation>;
export type UpdatePipelineVersionConfigMutationOptions = Apollo.BaseMutationOptions<UpdatePipelineVersionConfigMutation, UpdatePipelineVersionConfigMutationVariables>;
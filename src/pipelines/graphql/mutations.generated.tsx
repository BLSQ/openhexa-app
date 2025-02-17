import * as Types from '../../graphql/types';

import { gql } from '@apollo/client';
import * as Apollo from '@apollo/client';
const defaultOptions = {} as const;
export type UpdatePipelineMutationVariables = Types.Exact<{
  input: Types.UpdateDagInput;
}>;


export type UpdatePipelineMutation = { __typename?: 'Mutation', updateDAG: { __typename?: 'UpdateDAGResult', success: boolean, errors: Array<Types.UpdateDagError>, dag?: { __typename?: 'DAG', id: string, label: string, description?: string | null, schedule?: string | null } | null } };

export type CreatePipelineTemplateVersionMutationVariables = Types.Exact<{
  input: Types.CreatePipelineTemplateVersionInput;
}>;


export type CreatePipelineTemplateVersionMutation = { __typename?: 'Mutation', createPipelineTemplateVersion: { __typename?: 'CreatePipelineTemplateVersionResult', success: boolean, errors?: Array<Types.CreatePipelineTemplateVersionError> | null, pipelineTemplate?: { __typename?: 'PipelineTemplate', name: string, code: string } | null } };

export type CreatePipelineFromTemplateVersionMutationVariables = Types.Exact<{
  input: Types.CreatePipelineFromTemplateVersionInput;
}>;


export type CreatePipelineFromTemplateVersionMutation = { __typename?: 'Mutation', createPipelineFromTemplateVersion: { __typename?: 'CreatePipelineFromTemplateVersionResult', success: boolean, errors?: Array<Types.CreatePipelineFromTemplateVersionError> | null, pipeline?: { __typename?: 'Pipeline', id: string, name?: string | null, code: string } | null } };

export type UpgradePipelineVersionFromTemplateMutationVariables = Types.Exact<{
  input: Types.UpgradePipelineVersionFromTemplateInput;
}>;


export type UpgradePipelineVersionFromTemplateMutation = { __typename?: 'Mutation', upgradePipelineVersionFromTemplate: { __typename?: 'UpgradePipelineVersionFromTemplateResult', success: boolean, errors: Array<Types.UpgradePipelineVersionFromTemplateError> } };


export const UpdatePipelineDocument = gql`
    mutation UpdatePipeline($input: UpdateDAGInput!) {
  updateDAG(input: $input) {
    success
    errors
    dag {
      id
      label
      description
      schedule
    }
  }
}
    `;
export type UpdatePipelineMutationFn = Apollo.MutationFunction<UpdatePipelineMutation, UpdatePipelineMutationVariables>;

/**
 * __useUpdatePipelineMutation__
 *
 * To run a mutation, you first call `useUpdatePipelineMutation` within a React component and pass it any options that fit your needs.
 * When your component renders, `useUpdatePipelineMutation` returns a tuple that includes:
 * - A mutate function that you can call at any time to execute the mutation
 * - An object with fields that represent the current status of the mutation's execution
 *
 * @param baseOptions options that will be passed into the mutation, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options-2;
 *
 * @example
 * const [updatePipelineMutation, { data, loading, error }] = useUpdatePipelineMutation({
 *   variables: {
 *      input: // value for 'input'
 *   },
 * });
 */
export function useUpdatePipelineMutation(baseOptions?: Apollo.MutationHookOptions<UpdatePipelineMutation, UpdatePipelineMutationVariables>) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useMutation<UpdatePipelineMutation, UpdatePipelineMutationVariables>(UpdatePipelineDocument, options);
      }
export type UpdatePipelineMutationHookResult = ReturnType<typeof useUpdatePipelineMutation>;
export type UpdatePipelineMutationResult = Apollo.MutationResult<UpdatePipelineMutation>;
export type UpdatePipelineMutationOptions = Apollo.BaseMutationOptions<UpdatePipelineMutation, UpdatePipelineMutationVariables>;
export const CreatePipelineTemplateVersionDocument = gql`
    mutation CreatePipelineTemplateVersion($input: CreatePipelineTemplateVersionInput!) {
  createPipelineTemplateVersion(input: $input) {
    success
    errors
    pipelineTemplate {
      name
      code
    }
  }
}
    `;
export type CreatePipelineTemplateVersionMutationFn = Apollo.MutationFunction<CreatePipelineTemplateVersionMutation, CreatePipelineTemplateVersionMutationVariables>;

/**
 * __useCreatePipelineTemplateVersionMutation__
 *
 * To run a mutation, you first call `useCreatePipelineTemplateVersionMutation` within a React component and pass it any options that fit your needs.
 * When your component renders, `useCreatePipelineTemplateVersionMutation` returns a tuple that includes:
 * - A mutate function that you can call at any time to execute the mutation
 * - An object with fields that represent the current status of the mutation's execution
 *
 * @param baseOptions options that will be passed into the mutation, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options-2;
 *
 * @example
 * const [createPipelineTemplateVersionMutation, { data, loading, error }] = useCreatePipelineTemplateVersionMutation({
 *   variables: {
 *      input: // value for 'input'
 *   },
 * });
 */
export function useCreatePipelineTemplateVersionMutation(baseOptions?: Apollo.MutationHookOptions<CreatePipelineTemplateVersionMutation, CreatePipelineTemplateVersionMutationVariables>) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useMutation<CreatePipelineTemplateVersionMutation, CreatePipelineTemplateVersionMutationVariables>(CreatePipelineTemplateVersionDocument, options);
      }
export type CreatePipelineTemplateVersionMutationHookResult = ReturnType<typeof useCreatePipelineTemplateVersionMutation>;
export type CreatePipelineTemplateVersionMutationResult = Apollo.MutationResult<CreatePipelineTemplateVersionMutation>;
export type CreatePipelineTemplateVersionMutationOptions = Apollo.BaseMutationOptions<CreatePipelineTemplateVersionMutation, CreatePipelineTemplateVersionMutationVariables>;
export const CreatePipelineFromTemplateVersionDocument = gql`
    mutation CreatePipelineFromTemplateVersion($input: CreatePipelineFromTemplateVersionInput!) {
  createPipelineFromTemplateVersion(input: $input) {
    success
    errors
    pipeline {
      id
      name
      code
    }
  }
}
    `;
export type CreatePipelineFromTemplateVersionMutationFn = Apollo.MutationFunction<CreatePipelineFromTemplateVersionMutation, CreatePipelineFromTemplateVersionMutationVariables>;

/**
 * __useCreatePipelineFromTemplateVersionMutation__
 *
 * To run a mutation, you first call `useCreatePipelineFromTemplateVersionMutation` within a React component and pass it any options that fit your needs.
 * When your component renders, `useCreatePipelineFromTemplateVersionMutation` returns a tuple that includes:
 * - A mutate function that you can call at any time to execute the mutation
 * - An object with fields that represent the current status of the mutation's execution
 *
 * @param baseOptions options that will be passed into the mutation, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options-2;
 *
 * @example
 * const [createPipelineFromTemplateVersionMutation, { data, loading, error }] = useCreatePipelineFromTemplateVersionMutation({
 *   variables: {
 *      input: // value for 'input'
 *   },
 * });
 */
export function useCreatePipelineFromTemplateVersionMutation(baseOptions?: Apollo.MutationHookOptions<CreatePipelineFromTemplateVersionMutation, CreatePipelineFromTemplateVersionMutationVariables>) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useMutation<CreatePipelineFromTemplateVersionMutation, CreatePipelineFromTemplateVersionMutationVariables>(CreatePipelineFromTemplateVersionDocument, options);
      }
export type CreatePipelineFromTemplateVersionMutationHookResult = ReturnType<typeof useCreatePipelineFromTemplateVersionMutation>;
export type CreatePipelineFromTemplateVersionMutationResult = Apollo.MutationResult<CreatePipelineFromTemplateVersionMutation>;
export type CreatePipelineFromTemplateVersionMutationOptions = Apollo.BaseMutationOptions<CreatePipelineFromTemplateVersionMutation, CreatePipelineFromTemplateVersionMutationVariables>;
export const UpgradePipelineVersionFromTemplateDocument = gql`
    mutation upgradePipelineVersionFromTemplate($input: UpgradePipelineVersionFromTemplateInput!) {
  upgradePipelineVersionFromTemplate(input: $input) {
    success
    errors
  }
}
    `;
export type UpgradePipelineVersionFromTemplateMutationFn = Apollo.MutationFunction<UpgradePipelineVersionFromTemplateMutation, UpgradePipelineVersionFromTemplateMutationVariables>;

/**
 * __useUpgradePipelineVersionFromTemplateMutation__
 *
 * To run a mutation, you first call `useUpgradePipelineVersionFromTemplateMutation` within a React component and pass it any options that fit your needs.
 * When your component renders, `useUpgradePipelineVersionFromTemplateMutation` returns a tuple that includes:
 * - A mutate function that you can call at any time to execute the mutation
 * - An object with fields that represent the current status of the mutation's execution
 *
 * @param baseOptions options that will be passed into the mutation, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options-2;
 *
 * @example
 * const [upgradePipelineVersionFromTemplateMutation, { data, loading, error }] = useUpgradePipelineVersionFromTemplateMutation({
 *   variables: {
 *      input: // value for 'input'
 *   },
 * });
 */
export function useUpgradePipelineVersionFromTemplateMutation(baseOptions?: Apollo.MutationHookOptions<UpgradePipelineVersionFromTemplateMutation, UpgradePipelineVersionFromTemplateMutationVariables>) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useMutation<UpgradePipelineVersionFromTemplateMutation, UpgradePipelineVersionFromTemplateMutationVariables>(UpgradePipelineVersionFromTemplateDocument, options);
      }
export type UpgradePipelineVersionFromTemplateMutationHookResult = ReturnType<typeof useUpgradePipelineVersionFromTemplateMutation>;
export type UpgradePipelineVersionFromTemplateMutationResult = Apollo.MutationResult<UpgradePipelineVersionFromTemplateMutation>;
export type UpgradePipelineVersionFromTemplateMutationOptions = Apollo.BaseMutationOptions<UpgradePipelineVersionFromTemplateMutation, UpgradePipelineVersionFromTemplateMutationVariables>;
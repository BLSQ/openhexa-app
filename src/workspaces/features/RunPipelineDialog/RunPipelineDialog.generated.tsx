import * as Types from '../../../graphql-types';

import { gql } from '@apollo/client';
import { ParameterField_ParameterFragmentDoc } from './ParameterField.generated';
import { PipelineVersionPicker_PipelineFragmentDoc } from '../PipelineVersionPicker/PipelineVersionPicker.generated';
export type RunPipelineDialog_PipelineFragment = { __typename?: 'Pipeline', id: string, permissions: { __typename?: 'PipelinePermissions', run: boolean }, currentVersion?: { __typename?: 'PipelineVersion', id: string, number: number, createdAt: any, parameters: Array<{ __typename?: 'PipelineParameter', name: string, code: string, required: boolean, help?: string | null, type: string, default?: any | null, choices?: Array<any> | null, multiple: boolean }>, user?: { __typename?: 'User', displayName: string } | null } | null };

export type RunPipelineDialog_VersionFragment = { __typename?: 'PipelineVersion', id: string, number: number, createdAt: any, user?: { __typename?: 'User', displayName: string } | null, parameters: Array<{ __typename?: 'PipelineParameter', code: string, name: string, help?: string | null, type: string, default?: any | null, required: boolean, choices?: Array<any> | null, multiple: boolean }> };

export type RunPipelineDialog_RunFragment = { __typename?: 'PipelineRun', id: string, config: any, version: { __typename?: 'PipelineVersion', id: string, number: number, createdAt: any, parameters: Array<{ __typename?: 'PipelineParameter', code: string, name: string, help?: string | null, type: string, default?: any | null, required: boolean, choices?: Array<any> | null, multiple: boolean }>, user?: { __typename?: 'User', displayName: string } | null } };

export const RunPipelineDialog_PipelineFragmentDoc = gql`
    fragment RunPipelineDialog_pipeline on Pipeline {
  id
  permissions {
    run
  }
  currentVersion {
    id
    number
    createdAt
    parameters {
      name
      code
      required
      ...ParameterField_parameter
    }
    user {
      displayName
    }
  }
  ...PipelineVersionPicker_pipeline
}
    ${ParameterField_ParameterFragmentDoc}
${PipelineVersionPicker_PipelineFragmentDoc}`;
export const RunPipelineDialog_VersionFragmentDoc = gql`
    fragment RunPipelineDialog_version on PipelineVersion {
  id
  number
  createdAt
  user {
    displayName
  }
  parameters {
    ...ParameterField_parameter
  }
}
    ${ParameterField_ParameterFragmentDoc}`;
export const RunPipelineDialog_RunFragmentDoc = gql`
    fragment RunPipelineDialog_run on PipelineRun {
  id
  config
  version {
    id
    number
    createdAt
    parameters {
      ...ParameterField_parameter
    }
    user {
      displayName
    }
  }
}
    ${ParameterField_ParameterFragmentDoc}`;
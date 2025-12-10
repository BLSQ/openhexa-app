import * as Types from '../../../graphql/types';

import { gql } from '@apollo/client';
import { ParameterField_ParameterFragmentDoc } from './ParameterField.generated';
import { PipelineVersionPicker_PipelineFragmentDoc } from '../PipelineVersionPicker/PipelineVersionPicker.generated';
export type RunPipelineDialog_VersionFragment = { __typename?: 'PipelineVersion', id: string, versionName: string, createdAt: any, config?: any | null, user?: { __typename?: 'User', displayName: string } | null, parameters: Array<{ __typename?: 'PipelineParameter', code: string, name: string, help?: string | null, type: Types.ParameterType, default?: any | null, required: boolean, choices?: Array<any> | null, connection?: string | null, widget?: Types.ParameterWidget | null, multiple: boolean, directory?: string | null }> };

export type RunPipelineDialog_PipelineFragment = { __typename?: 'Pipeline', id: string, code: string, type: Types.PipelineType, workspace: { __typename?: 'Workspace', slug: string }, permissions: { __typename?: 'PipelinePermissions', run: boolean }, currentVersion?: { __typename?: 'PipelineVersion', id: string, versionName: string, createdAt: any, config?: any | null, user?: { __typename?: 'User', displayName: string } | null, parameters: Array<{ __typename?: 'PipelineParameter', code: string, name: string, help?: string | null, type: Types.ParameterType, default?: any | null, required: boolean, choices?: Array<any> | null, connection?: string | null, widget?: Types.ParameterWidget | null, multiple: boolean, directory?: string | null }> } | null };

export type RunPipelineDialog_RunFragment = { __typename?: 'PipelineRun', id: string, config: any, version?: { __typename?: 'PipelineVersion', id: string, versionName: string, createdAt: any, parameters: Array<{ __typename?: 'PipelineParameter', code: string, name: string, help?: string | null, type: Types.ParameterType, default?: any | null, required: boolean, choices?: Array<any> | null, connection?: string | null, widget?: Types.ParameterWidget | null, multiple: boolean, directory?: string | null }>, user?: { __typename?: 'User', displayName: string } | null } | null };

export const RunPipelineDialog_VersionFragmentDoc = gql`
    fragment RunPipelineDialog_version on PipelineVersion {
  id
  versionName
  createdAt
  config
  user {
    displayName
  }
  parameters {
    ...ParameterField_parameter
  }
}
    ${ParameterField_ParameterFragmentDoc}`;
export const RunPipelineDialog_PipelineFragmentDoc = gql`
    fragment RunPipelineDialog_pipeline on Pipeline {
  id
  workspace {
    slug
  }
  permissions {
    run
  }
  code
  type
  currentVersion {
    id
    versionName
    createdAt
    config
    user {
      displayName
    }
    parameters {
      ...ParameterField_parameter
    }
  }
  ...PipelineVersionPicker_pipeline
}
    ${ParameterField_ParameterFragmentDoc}
${PipelineVersionPicker_PipelineFragmentDoc}`;
export const RunPipelineDialog_RunFragmentDoc = gql`
    fragment RunPipelineDialog_run on PipelineRun {
  id
  config
  version {
    id
    versionName
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
import * as Types from '../../../graphql-types';

import { gql } from '@apollo/client';
import { PipelineVersionPicker_PipelineFragmentDoc } from '../PipelineVersionPicker/PipelineVersionPicker.generated';
export type RunPipelineDialog_PipelineFragment = { __typename?: 'Pipeline', id: string, permissions: { __typename?: 'PipelinePermissions', run: boolean }, currentVersion?: { __typename?: 'PipelineVersion', id: string, number: number, createdAt: any, parameters: any, user?: { __typename?: 'User', displayName: string } | null } | null, versions: { __typename?: 'PipelineVersionPage', items: Array<{ __typename?: 'PipelineVersion', id: string, number: number, createdAt: any, parameters: any, user?: { __typename?: 'User', displayName: string } | null }> } };

export type RunPipelineDialog_VersionFragment = { __typename?: 'PipelineVersion', id: string, number: number, createdAt: any, parameters: any, user?: { __typename?: 'User', displayName: string } | null };

export type RunPipelineDialog_RunFragment = { __typename?: 'PipelineRun', id: string, config: any, version: { __typename?: 'PipelineVersion', id: string, number: number, createdAt: any, parameters: any, user?: { __typename?: 'User', displayName: string } | null } };

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
    parameters
    user {
      displayName
    }
  }
  ...PipelineVersionPicker_pipeline
}
    ${PipelineVersionPicker_PipelineFragmentDoc}`;
export const RunPipelineDialog_VersionFragmentDoc = gql`
    fragment RunPipelineDialog_version on PipelineVersion {
  id
  number
  createdAt
  user {
    displayName
  }
  parameters
}
    `;
export const RunPipelineDialog_RunFragmentDoc = gql`
    fragment RunPipelineDialog_run on PipelineRun {
  id
  config
  version {
    id
    number
    createdAt
    parameters
    user {
      displayName
    }
  }
}
    `;
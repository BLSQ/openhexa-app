import * as Types from '../../../graphql/types';

import { gql } from '@apollo/client';
export type PipelineVersionPicker_PipelineFragment = { __typename?: 'Pipeline', id: string };

export type PipelineVersionPicker_VersionFragment = { __typename?: 'PipelineVersion', id: string, versionName: string, createdAt: any, config?: any | null, parameters: Array<{ __typename?: 'PipelineParameter', code: string, name: string, help?: string | null, type: Types.ParameterType, widget?: Types.ParameterWidget | null, connection?: string | null, default?: any | null, required: boolean, choices?: Array<any> | null, multiple: boolean }>, user?: { __typename?: 'User', displayName: string } | null };

export const PipelineVersionPicker_PipelineFragmentDoc = gql`
    fragment PipelineVersionPicker_pipeline on Pipeline {
  id
}
    `;
export const PipelineVersionPicker_VersionFragmentDoc = gql`
    fragment PipelineVersionPicker_version on PipelineVersion {
  id
  versionName
  createdAt
  config
  parameters {
    code
    name
    help
    type
    widget
    connection
    default
    required
    choices
    multiple
  }
  user {
    displayName
  }
}
    `;
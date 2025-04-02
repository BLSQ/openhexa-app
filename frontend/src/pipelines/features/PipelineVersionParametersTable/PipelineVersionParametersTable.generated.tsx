import * as Types from '../../../graphql/types';

import { gql } from '@apollo/client';
export type PipelineVersionParametersTable_VersionFragment = { __typename?: 'PipelineVersion', id: string, config?: any | null, parameters: Array<{ __typename?: 'PipelineParameter', code: string, name: string, multiple: boolean, type: Types.ParameterType, help?: string | null, required: boolean, choices?: Array<any> | null }> };

export const PipelineVersionParametersTable_VersionFragmentDoc = gql`
    fragment PipelineVersionParametersTable_version on PipelineVersion {
  id
  parameters {
    code
    name
    multiple
    type
    help
    required
    choices
  }
  config
}
    `;
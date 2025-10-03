import * as Types from '../../../graphql/types';

import { gql } from '@apollo/client';
import { ParameterField_ParameterFragmentDoc } from '../../../workspaces/features/RunPipelineDialog/ParameterField.generated';
export type PipelineVersionParametersTable_VersionFragment = { __typename?: 'PipelineVersion', id: string, config?: any | null, parameters: Array<{ __typename?: 'PipelineParameter', code: string, name: string, help?: string | null, type: Types.ParameterType, default?: any | null, required: boolean, choices?: Array<any> | null, connection?: string | null, widget?: Types.ParameterWidget | null, multiple: boolean, directory?: string | null }> };

export const PipelineVersionParametersTable_VersionFragmentDoc = gql`
    fragment PipelineVersionParametersTable_version on PipelineVersion {
  id
  parameters {
    ...ParameterField_parameter
  }
  config
}
    ${ParameterField_ParameterFragmentDoc}`;
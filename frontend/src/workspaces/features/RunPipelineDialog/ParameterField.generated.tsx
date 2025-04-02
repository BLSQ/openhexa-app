import * as Types from '../../../graphql/types';

import { gql } from '@apollo/client';
export type ParameterField_ParameterFragment = { __typename?: 'PipelineParameter', code: string, name: string, help?: string | null, type: Types.ParameterType, default?: any | null, required: boolean, choices?: Array<any> | null, connection?: string | null, widget?: Types.ParameterWidget | null, multiple: boolean };

export const ParameterField_ParameterFragmentDoc = gql`
    fragment ParameterField_parameter on PipelineParameter {
  code
  name
  help
  type
  default
  required
  choices
  connection
  widget
  multiple
}
    `;
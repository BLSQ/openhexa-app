import * as Types from '../../../graphql/types';

import { gql } from '@apollo/client';
export type PipelineDagView_VersionFragment = { __typename?: 'PipelineVersion', id: string, parameters: Array<{ __typename?: 'PipelineParameter', code: string, name: string, type: Types.ParameterType, required: boolean }>, dag: { __typename?: 'PipelineDag', tasks: Array<{ __typename?: 'PipelineDagTask', id: string, name: string }>, edges: Array<{ __typename?: 'PipelineDagEdge', source: string, target: string }> } };

export const PipelineDagView_VersionFragmentDoc = gql`
    fragment PipelineDagView_version on PipelineVersion {
  id
  parameters {
    code
    name
    type
    required
  }
  dag {
    tasks {
      id
      name
    }
    edges {
      source
      target
    }
  }
}
    `;
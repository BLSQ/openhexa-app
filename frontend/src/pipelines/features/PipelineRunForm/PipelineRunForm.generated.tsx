import * as Types from '../../../graphql/types';

import { gql } from '@apollo/client';
export type PipelineRunForm_DagFragment = { __typename?: 'DAG', formCode?: string | null, id: string, template: { __typename?: 'DAGTemplate', sampleConfig?: any | null } };

export const PipelineRunForm_DagFragmentDoc = gql`
    fragment PipelineRunForm_dag on DAG {
  template {
    sampleConfig
  }
  formCode
  id
}
    `;
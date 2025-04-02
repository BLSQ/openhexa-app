import * as Types from '../../../graphql/types';

import { gql } from '@apollo/client';
export type PipelineRunReadonlyForm_DagFragment = { __typename?: 'DAG', formCode?: string | null, id: string };

export type PipelineRunReadonlyForm_DagRunFragment = { __typename?: 'DAGRun', config?: any | null };

export const PipelineRunReadonlyForm_DagFragmentDoc = gql`
    fragment PipelineRunReadonlyForm_dag on DAG {
  formCode
  id
}
    `;
export const PipelineRunReadonlyForm_DagRunFragmentDoc = gql`
    fragment PipelineRunReadonlyForm_dagRun on DAGRun {
  config
}
    `;
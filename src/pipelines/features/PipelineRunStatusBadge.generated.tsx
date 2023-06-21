import * as Types from '../../graphql-types';

import { gql } from '@apollo/client';
export type PipelineRunStatusBadge_DagRunFragment = { __typename?: 'DAGRun', status: Types.DagRunStatus };

export type PipelineRunStatusBadge_RunFragment = { __typename?: 'PipelineRun', id: string, status: Types.PipelineRunStatus };

export const PipelineRunStatusBadge_DagRunFragmentDoc = gql`
    fragment PipelineRunStatusBadge_dagRun on DAGRun {
  status
}
    `;
export const PipelineRunStatusBadge_RunFragmentDoc = gql`
    fragment PipelineRunStatusBadge_run on PipelineRun {
  id
  status
}
    `;
import * as Types from '../../../graphql/types';

import { gql } from '@apollo/client';
export type RunLogs_DagRunFragment = { __typename?: 'DAGRun', id: string, logs?: string | null, status: Types.DagRunStatus };

export type RunLogs_RunFragment = { __typename?: 'PipelineRun', id: string, logs?: string | null, status: Types.PipelineRunStatus };

export const RunLogs_DagRunFragmentDoc = gql`
    fragment RunLogs_dagRun on DAGRun {
  id
  logs
  status
}
    `;
export const RunLogs_RunFragmentDoc = gql`
    fragment RunLogs_run on PipelineRun {
  id
  logs
  status
}
    `;
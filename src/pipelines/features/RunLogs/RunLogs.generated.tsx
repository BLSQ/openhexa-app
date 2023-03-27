import * as Types from '../../../graphql-types';

import { gql } from '@apollo/client';
export type RunLogs_DagRunFragment = { __typename?: 'DAGRun', id: string, logs?: string | null };

export type RunLogs_RunFragment = { __typename?: 'PipelineRun', id: string, logs?: string | null };

export const RunLogs_DagRunFragmentDoc = gql`
    fragment RunLogs_dagRun on DAGRun {
  id
  logs
}
    `;
export const RunLogs_RunFragmentDoc = gql`
    fragment RunLogs_run on PipelineRun {
  id
  logs
}
    `;
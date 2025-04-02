import * as Types from '../../../graphql/types';

import { gql } from '@apollo/client';
export type RunMessages_DagRunFragment = { __typename?: 'DAGRun', id: string, status: Types.DagRunStatus, messages: Array<{ __typename?: 'DAGRunMessage', message: string, timestamp?: any | null, priority: string }> };

export type RunMessages_RunFragment = { __typename?: 'PipelineRun', id: string, status: Types.PipelineRunStatus, messages: Array<{ __typename?: 'PipelineRunMessage', message: string, timestamp?: any | null, priority: Types.MessagePriority }> };

export const RunMessages_DagRunFragmentDoc = gql`
    fragment RunMessages_dagRun on DAGRun {
  id
  status
  messages {
    message
    timestamp
    priority
  }
}
    `;
export const RunMessages_RunFragmentDoc = gql`
    fragment RunMessages_run on PipelineRun {
  id
  status
  messages {
    message
    timestamp
    priority
  }
}
    `;
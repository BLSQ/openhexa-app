import * as Types from '../../../graphql-types';

import { gql } from '@apollo/client';
export type RunMessages_DagRunFragment = { __typename?: 'DAGRun', id: string, messages: Array<{ __typename?: 'DAGRunMessage', message: string, timestamp?: any | null, priority: string }> };

export const RunMessages_DagRunFragmentDoc = gql`
    fragment RunMessages_dagRun on DAGRun {
  id
  messages {
    message
    timestamp
    priority
  }
}
    `;
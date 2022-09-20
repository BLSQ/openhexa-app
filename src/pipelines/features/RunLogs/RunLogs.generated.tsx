import * as Types from '../../../graphql-types';

import { gql } from '@apollo/client';
export type RunLogs_DagRunFragment = { __typename?: 'DAGRun', id: string, logs?: string | null };

export const RunLogs_DagRunFragmentDoc = gql`
    fragment RunLogs_dagRun on DAGRun {
  id
  logs
}
    `;
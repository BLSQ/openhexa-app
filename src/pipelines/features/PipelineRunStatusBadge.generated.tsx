import * as Types from '../../graphql-types';

import { gql } from '@apollo/client';
export type PipelineRunStatusBadge_DagRunFragment = { __typename?: 'DAGRun', status: Types.DagRunStatus };

export const PipelineRunStatusBadge_DagRunFragmentDoc = gql`
    fragment PipelineRunStatusBadge_dagRun on DAGRun {
  status
}
    `;
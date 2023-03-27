import * as Types from '../../../graphql-types';

import { gql } from '@apollo/client';
import { PipelineRunStatusBadge_RunFragmentDoc } from '../../../pipelines/features/PipelineRunStatusBadge.generated';
export type PipelineCard_PipelineFragment = { __typename?: 'Pipeline', id: string, name: string, schedule?: string | null, description?: string | null, lastRuns: { __typename?: 'PipelineRunPage', items: Array<{ __typename?: 'PipelineRun', status: Types.PipelineRunStatus }> } };

export type PipelineCard_WorkspaceFragment = { __typename?: 'Workspace', slug: string };

export const PipelineCard_PipelineFragmentDoc = gql`
    fragment PipelineCard_pipeline on Pipeline {
  id
  name
  schedule
  description
  lastRuns: runs(orderBy: EXECUTION_DATE_DESC, page: 1, perPage: 1) {
    items {
      ...PipelineRunStatusBadge_run
    }
  }
}
    ${PipelineRunStatusBadge_RunFragmentDoc}`;
export const PipelineCard_WorkspaceFragmentDoc = gql`
    fragment PipelineCard_workspace on Workspace {
  slug
}
    `;
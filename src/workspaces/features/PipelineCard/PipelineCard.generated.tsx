import * as Types from '../../../graphql/types';

import { gql } from '@apollo/client';
import { PipelineRunStatusBadge_RunFragmentDoc } from '../../../pipelines/features/PipelineRunStatusBadge.generated';
export type PipelineCard_PipelineFragment = { __typename?: 'Pipeline', id: string, code: string, name?: string | null, schedule?: string | null, description?: string | null, type: Types.PipelineType, lastRuns: { __typename?: 'PipelineRunPage', items: Array<{ __typename?: 'PipelineRun', id: string, status: Types.PipelineRunStatus }> } };

export type PipelineCard_WorkspaceFragment = { __typename?: 'Workspace', slug: string };

export const PipelineCard_PipelineFragmentDoc = gql`
    fragment PipelineCard_pipeline on Pipeline {
  id
  code
  name
  schedule
  description
  type
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
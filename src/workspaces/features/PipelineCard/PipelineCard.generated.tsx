import * as Types from '../../../graphql/types';

import { gql } from '@apollo/client';
import { User_UserFragmentDoc } from '../../../core/features/User/User.generated';
import { PipelineRunStatusBadge_RunFragmentDoc } from '../../../pipelines/features/PipelineRunStatusBadge.generated';
export type PipelineCard_PipelineFragment = { __typename?: 'Pipeline', id: string, code: string, name?: string | null, schedule?: string | null, description?: string | null, type: Types.PipelineType, currentVersion?: { __typename?: 'PipelineVersion', createdAt: any, user?: { __typename?: 'User', id: string, email: string, displayName: string, avatar: { __typename?: 'Avatar', initials: string, color: string } } | null } | null, lastRuns: { __typename?: 'PipelineRunPage', items: Array<{ __typename?: 'PipelineRun', id: string, status: Types.PipelineRunStatus }> } };

export type PipelineCard_WorkspaceFragment = { __typename?: 'Workspace', slug: string };

export const PipelineCard_PipelineFragmentDoc = gql`
    fragment PipelineCard_pipeline on Pipeline {
  id
  code
  name
  schedule
  description
  type
  currentVersion {
    user {
      ...User_user
    }
    createdAt
  }
  lastRuns: runs(orderBy: EXECUTION_DATE_DESC, page: 1, perPage: 1) {
    items {
      ...PipelineRunStatusBadge_run
    }
  }
}
    ${User_UserFragmentDoc}
${PipelineRunStatusBadge_RunFragmentDoc}`;
export const PipelineCard_WorkspaceFragmentDoc = gql`
    fragment PipelineCard_workspace on Workspace {
  slug
}
    `;
import * as Types from '../../../graphql/types';

import { gql } from '@apollo/client';
import { Tag_TagFragmentDoc } from '../Tag.generated';
import { WorkspaceDisplayFragmentFragmentDoc } from './WorkspaceDisplay.generated';
import { PipelineRunStatusBadge_RunFragmentDoc } from '../../../pipelines/features/PipelineRunStatusBadge.generated';
export type PipelinesPageFragment = { __typename?: 'PipelineResultPage', totalItems: number, pageNumber: number, totalPages: number, items: Array<{ __typename?: 'PipelineResult', score: number, pipeline: { __typename?: 'Pipeline', id: string, code: string, name?: string | null, description?: string | null, updatedAt?: any | null, tags: Array<{ __typename?: 'Tag', id: string, name: string }>, workspace: { __typename?: 'Workspace', slug: string, name: string, countries: Array<{ __typename?: 'Country', code: string }> }, lastRuns: { __typename?: 'PipelineRunPage', items: Array<{ __typename?: 'PipelineRun', id: string, status: Types.PipelineRunStatus }> } } }> };

export const PipelinesPageFragmentDoc = gql`
    fragment PipelinesPage on PipelineResultPage {
  items {
    pipeline {
      id
      code
      name
      description
      updatedAt
      tags {
        ...Tag_tag
      }
      workspace {
        slug
        ...WorkspaceDisplayFragment
      }
      lastRuns: runs(orderBy: EXECUTION_DATE_DESC, page: 1, perPage: 1) {
        items {
          ...PipelineRunStatusBadge_run
        }
      }
    }
    score
  }
  totalItems
  pageNumber
  totalPages
}
    ${Tag_TagFragmentDoc}
${WorkspaceDisplayFragmentFragmentDoc}
${PipelineRunStatusBadge_RunFragmentDoc}`;
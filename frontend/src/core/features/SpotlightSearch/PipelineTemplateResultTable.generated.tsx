import * as Types from '../../../graphql/types';

import { gql } from '@apollo/client';
import { WorkspaceDisplayFragmentFragmentDoc } from './WorkspaceDisplay.generated';
export type PipelineTemplatesPageFragment = { __typename?: 'PipelineTemplateResultPage', totalItems: number, pageNumber: number, totalPages: number, items: Array<{ __typename?: 'PipelineTemplateResult', score: number, pipelineTemplate: { __typename?: 'PipelineTemplate', id: string, code: string, name: string, description?: string | null, updatedAt?: any | null, workspace: { __typename?: 'Workspace', slug: string, name: string, countries: Array<{ __typename?: 'Country', code: string }> }, currentVersion?: { __typename?: 'PipelineTemplateVersion', id: string, versionNumber: number } | null } }> };

export const PipelineTemplatesPageFragmentDoc = gql`
    fragment PipelineTemplatesPage on PipelineTemplateResultPage {
  items {
    pipelineTemplate {
      id
      code
      name
      description
      workspace {
        slug
        ...WorkspaceDisplayFragment
      }
      currentVersion {
        id
        versionNumber
      }
      updatedAt
    }
    score
  }
  totalItems
  pageNumber
  totalPages
}
    ${WorkspaceDisplayFragmentFragmentDoc}`;
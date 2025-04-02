import * as Types from '../../../graphql/types';

import { gql } from '@apollo/client';
export type UpgradePipelineFromTemplateDialog_PipelineFragment = { __typename?: 'Pipeline', id: string, code: string, newTemplateVersions: Array<{ __typename?: 'PipelineTemplateVersion', id: string, versionNumber: number, changelog?: string | null, createdAt: any }> };

export const UpgradePipelineFromTemplateDialog_PipelineFragmentDoc = gql`
    fragment UpgradePipelineFromTemplateDialog_pipeline on Pipeline {
  id
  code
  newTemplateVersions {
    id
    versionNumber
    changelog
    createdAt
  }
}
    `;
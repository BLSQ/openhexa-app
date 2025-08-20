import * as Types from '../../../graphql/types';

import { gql } from '@apollo/client';
import { DownloadPipelineVersion_VersionFragmentDoc } from '../DownloadPipelineVersion/DownloadPipelineVersion.generated';
import { DeletePipelineVersionTrigger_VersionFragmentDoc } from '../../../workspaces/features/DeletePipelineVersionTrigger/DeletePipelineVersionTrigger.generated';
export type PipelineVersionCard_VersionFragment = { __typename?: 'PipelineVersion', id: string, versionName: string, name?: string | null, description?: string | null, externalLink?: any | null, isLatestVersion: boolean, createdAt: any, user?: { __typename?: 'User', displayName: string } | null, permissions: { __typename?: 'PipelineVersionPermissions', update: boolean, delete: boolean }, parameters: Array<{ __typename?: 'PipelineParameter', code: string, name: string, type: Types.ParameterType, multiple: boolean, required: boolean, help?: string | null }>, pipeline: { __typename?: 'Pipeline', id: string, code: string }, templateVersion?: { __typename?: 'PipelineTemplateVersion', id: string, versionNumber: number, template: { __typename?: 'PipelineTemplate', id: string, name: string } } | null };

export const PipelineVersionCard_VersionFragmentDoc = gql`
    fragment PipelineVersionCard_version on PipelineVersion {
  id
  versionName
  name
  description
  externalLink
  isLatestVersion
  createdAt
  user {
    displayName
  }
  permissions {
    update
  }
  parameters {
    code
    name
    type
    multiple
    required
    help
  }
  pipeline {
    id
    code
  }
  templateVersion {
    id
    versionNumber
    template {
      id
      name
    }
  }
  ...DownloadPipelineVersion_version
  ...DeletePipelineVersionTrigger_version
}
    ${DownloadPipelineVersion_VersionFragmentDoc}
${DeletePipelineVersionTrigger_VersionFragmentDoc}`;
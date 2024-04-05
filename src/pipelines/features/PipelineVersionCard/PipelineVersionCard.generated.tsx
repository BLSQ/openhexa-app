import * as Types from '../../../graphql-types';

import { gql } from '@apollo/client';
import { DownloadPipelineVersion_VersionFragmentDoc } from '../DownloadPipelineVersion/DownloadPipelineVersion.generated';
export type PipelineVersionCard_VersionFragment = { __typename?: 'PipelineVersion', id: string, name: string, description?: string | null, externalLink?: any | null, isLatestVersion: boolean, createdAt: any, user?: { __typename?: 'User', displayName: string } | null, parameters: Array<{ __typename?: 'PipelineParameter', code: string, name: string, type: string, multiple: boolean, required: boolean, help?: string | null }>, pipeline: { __typename?: 'Pipeline', id: string, code: string } };

export const PipelineVersionCard_VersionFragmentDoc = gql`
    fragment PipelineVersionCard_version on PipelineVersion {
  id
  name
  description
  externalLink
  isLatestVersion
  createdAt
  user {
    displayName
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
  ...DownloadPipelineVersion_version
}
    ${DownloadPipelineVersion_VersionFragmentDoc}`;
import * as Types from '../../../graphql/types';

import { gql } from '@apollo/client';
export type DownloadTemplateVersion_VersionFragment = { __typename?: 'PipelineTemplateVersion', id: string, versionNumber: number, template: { __typename?: 'PipelineTemplate', code: string }, sourcePipelineVersion: { __typename?: 'PipelineVersion', zipfile: string } };

export const DownloadTemplateVersion_VersionFragmentDoc = gql`
    fragment DownloadTemplateVersion_version on PipelineTemplateVersion {
  id
  versionNumber
  template {
    code
  }
  sourcePipelineVersion {
    zipfile
  }
}
    `;
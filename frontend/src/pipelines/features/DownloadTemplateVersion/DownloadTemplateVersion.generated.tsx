import * as Types from '../../../graphql/types';

import { gql } from '@apollo/client';
export type DownloadTemplateVersion_VersionFragment = { __typename?: 'PipelineTemplateVersion', id: string };

export const DownloadTemplateVersion_VersionFragmentDoc = gql`
    fragment DownloadTemplateVersion_version on PipelineTemplateVersion {
  id
}
    `;
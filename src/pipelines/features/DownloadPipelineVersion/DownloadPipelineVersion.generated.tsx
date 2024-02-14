import * as Types from '../../../graphql-types';

import { gql } from '@apollo/client';
export type DownloadPipelineVersion_VersionFragment = { __typename?: 'PipelineVersion', id: string, number: number, pipeline: { __typename?: 'Pipeline', id: string, code: string } };

export const DownloadPipelineVersion_VersionFragmentDoc = gql`
    fragment DownloadPipelineVersion_version on PipelineVersion {
  id
  number
  pipeline {
    id
    code
  }
}
    `;
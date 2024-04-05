import * as Types from '../../../graphql-types';

import { gql } from '@apollo/client';
export type DeletePipelineVersion_PipelineFragment = { __typename?: 'Pipeline', id: string, code: string, name?: string | null };

export type DeletePipelineVersion_VersionFragment = { __typename?: 'PipelineVersion', id: string, name: string };

export const DeletePipelineVersion_PipelineFragmentDoc = gql`
    fragment DeletePipelineVersion_pipeline on Pipeline {
  id
  code
  name
}
    `;
export const DeletePipelineVersion_VersionFragmentDoc = gql`
    fragment DeletePipelineVersion_version on PipelineVersion {
  id
  name
}
    `;
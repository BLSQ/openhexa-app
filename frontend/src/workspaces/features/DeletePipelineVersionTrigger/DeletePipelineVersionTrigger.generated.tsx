import * as Types from '../../../graphql/types';

import { gql } from '@apollo/client';
export type DeletePipelineVersionTrigger_VersionFragment = { __typename?: 'PipelineVersion', id: string, name?: string | null, pipeline: { __typename?: 'Pipeline', id: string }, permissions: { __typename?: 'PipelineVersionPermissions', delete: boolean } };

export const DeletePipelineVersionTrigger_VersionFragmentDoc = gql`
    fragment DeletePipelineVersionTrigger_version on PipelineVersion {
  id
  name
  pipeline {
    id
  }
  permissions {
    delete
  }
}
    `;
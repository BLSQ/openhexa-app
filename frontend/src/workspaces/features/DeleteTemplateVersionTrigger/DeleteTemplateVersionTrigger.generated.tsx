import * as Types from '../../../graphql/types';

import { gql } from '@apollo/client';
export type DeleteTemplateVersionTrigger_VersionFragment = { __typename?: 'PipelineTemplateVersion', id: string, versionNumber: number, template: { __typename?: 'PipelineTemplate', id: string }, permissions: { __typename?: 'PipelineTemplateVersionPermissions', delete: boolean } };

export const DeleteTemplateVersionTrigger_VersionFragmentDoc = gql`
    fragment DeleteTemplateVersionTrigger_version on PipelineTemplateVersion {
  id
  versionNumber
  template {
    id
  }
  permissions {
    delete
  }
}
    `;
import * as Types from '../../../graphql/types';

import { gql } from '@apollo/client';
import { DeleteTemplateVersionTrigger_VersionFragmentDoc } from '../../../workspaces/features/DeleteTemplateVersionTrigger/DeleteTemplateVersionTrigger.generated';
export type TemplateVersionCard_VersionFragment = { __typename?: 'PipelineTemplateVersion', id: string, versionNumber: number, changelog?: string | null, createdAt: any, isLatestVersion: boolean, user?: { __typename?: 'User', displayName: string } | null, permissions: { __typename?: 'PipelineTemplateVersionPermissions', update: boolean, delete: boolean }, template: { __typename?: 'PipelineTemplate', id: string, code: string } };

export const TemplateVersionCard_VersionFragmentDoc = gql`
    fragment TemplateVersionCard_version on PipelineTemplateVersion {
  id
  versionNumber
  changelog
  createdAt
  isLatestVersion
  user {
    displayName
  }
  permissions {
    update
  }
  template {
    id
    code
  }
  ...DeleteTemplateVersionTrigger_version
}
    ${DeleteTemplateVersionTrigger_VersionFragmentDoc}`;
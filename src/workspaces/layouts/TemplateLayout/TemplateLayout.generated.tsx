import * as Types from '../../../graphql/types';

import { gql } from '@apollo/client';
import { TabLayout_WorkspaceFragmentDoc } from '../TabLayout/TabLayout.generated';
export type TemplateLayout_WorkspaceFragment = { __typename?: 'Workspace', name: string, slug: string, permissions: { __typename?: 'WorkspacePermissions', manageMembers: boolean, update: boolean, launchNotebookServer: boolean }, countries: Array<{ __typename?: 'Country', flag: string, code: string }> };

export type TemplateLayout_TemplateFragment = { __typename?: 'PipelineTemplate', id: string, code: string, name: string, permissions: { __typename?: 'PipelineTemplatePermissions', delete: boolean, update: boolean }, currentVersion?: { __typename?: 'PipelineTemplateVersion', id: string } | null };

export const TemplateLayout_WorkspaceFragmentDoc = gql`
    fragment TemplateLayout_workspace on Workspace {
  ...TabLayout_workspace
}
    ${TabLayout_WorkspaceFragmentDoc}`;
export const TemplateLayout_TemplateFragmentDoc = gql`
    fragment TemplateLayout_template on PipelineTemplate {
  id
  code
  name
  permissions {
    delete
    update
  }
  currentVersion {
    id
  }
}
    `;
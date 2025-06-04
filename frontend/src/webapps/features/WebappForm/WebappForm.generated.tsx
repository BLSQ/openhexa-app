import * as Types from '../../../graphql/types';

import { gql } from '@apollo/client';
import { WorkspaceLayout_WorkspaceFragmentDoc } from '../../../workspaces/layouts/WorkspaceLayout/WorkspaceLayout.generated';
export type WebappForm_WebappFragment = { __typename?: 'Webapp', id: string, name: string, description?: string | null, url: string, icon?: string | null, permissions: { __typename?: 'WebappPermissions', update: boolean, delete: boolean } };

export type WebappForm_WorkspaceFragment = { __typename?: 'Workspace', slug: string, name: string, permissions: { __typename?: 'WorkspacePermissions', manageMembers: boolean, update: boolean, launchNotebookServer: boolean }, countries: Array<{ __typename?: 'Country', flag: string, code: string }>, organization?: { __typename?: 'Organization', name: string } | null };

export const WebappForm_WebappFragmentDoc = gql`
    fragment WebappForm_webapp on Webapp {
  id
  name
  description
  url
  icon
  permissions {
    update
    delete
  }
}
    `;
export const WebappForm_WorkspaceFragmentDoc = gql`
    fragment WebappForm_workspace on Workspace {
  ...WorkspaceLayout_workspace
}
    ${WorkspaceLayout_WorkspaceFragmentDoc}`;
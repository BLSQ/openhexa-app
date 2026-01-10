import * as Types from '../../../graphql/types';

import { gql } from '@apollo/client';
import { WorkspaceLayout_WorkspaceFragmentDoc } from '../../../workspaces/layouts/WorkspaceLayout/WorkspaceLayout.generated';
export type WebappForm_WebappFragment = { __typename?: 'Webapp', id: string, slug: string, name: string, description?: string | null, url?: string | null, type: Types.WebappType, icon?: string | null, content?: string | null, isPublic: boolean, permissions: { __typename?: 'WebappPermissions', update: boolean, delete: boolean } };

export type WebappForm_WorkspaceFragment = { __typename?: 'Workspace', slug: string, name: string, permissions: { __typename?: 'WorkspacePermissions', manageMembers: boolean, update: boolean, launchNotebookServer: boolean }, shortcuts: Array<{ __typename?: 'ShortcutItem', id: string, name: string, url: string, order: number }>, countries: Array<{ __typename?: 'Country', flag: string, code: string }>, organization?: { __typename?: 'Organization', id: string, name: string, shortName?: string | null, logo?: string | null, permissions: { __typename?: 'OrganizationPermissions', createWorkspace: boolean } } | null };

export const WebappForm_WebappFragmentDoc = gql`
    fragment WebappForm_webapp on Webapp {
  id
  slug
  name
  description
  url
  type
  icon
  content
  isPublic
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
import * as Types from '../../../graphql/types';

import { gql } from '@apollo/client';
import { TabLayout_WorkspaceFragmentDoc } from '../TabLayout/TabLayout.generated';
export type WebappLayout_WorkspaceFragment = { __typename?: 'Workspace', slug: string, name: string, permissions: { __typename?: 'WorkspacePermissions', manageMembers: boolean, update: boolean, launchNotebookServer: boolean }, shortcuts: Array<{ __typename?: 'ShortcutItem', id: string, name: string, url: string, order: number }>, countries: Array<{ __typename?: 'Country', flag: string, code: string }>, organization?: { __typename?: 'Organization', id: string, name: string, shortName?: string | null, logo?: string | null, permissions: { __typename?: 'OrganizationPermissions', createWorkspace: { __typename?: 'CreateWorkspacePermission', isAllowed: boolean } } } | null };

export type WebappLayout_WebappFragment = { __typename?: 'Webapp', id: string, slug: string, name: string, url: string, type: Types.WebappType, permissions: { __typename?: 'WebappPermissions', update: boolean, delete: boolean } };

export const WebappLayout_WorkspaceFragmentDoc = gql`
    fragment WebappLayout_workspace on Workspace {
  slug
  ...TabLayout_workspace
}
    ${TabLayout_WorkspaceFragmentDoc}`;
export const WebappLayout_WebappFragmentDoc = gql`
    fragment WebappLayout_webapp on Webapp {
  id
  slug
  name
  url
  type
  permissions {
    update
    delete
  }
}
    `;
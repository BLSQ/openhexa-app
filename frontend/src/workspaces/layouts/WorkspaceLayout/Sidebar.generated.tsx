import * as Types from '../../../graphql/types';

import { gql } from '@apollo/client';
import { SidebarMenu_WorkspaceFragmentDoc } from '../../features/SidebarMenu/SidebarMenu.generated';
export type Sidebar_WorkspaceFragment = { __typename?: 'Workspace', slug: string, name: string, permissions: { __typename?: 'WorkspacePermissions', manageMembers: boolean, update: boolean, launchNotebookServer: boolean }, shortcuts: Array<{ __typename?: 'ShortcutItem', id: string, name: string, url: string, order: number }>, countries: Array<{ __typename?: 'Country', flag: string, code: string }>, organization?: { __typename?: 'Organization', id: string, name: string, shortName?: string | null, permissions: { __typename?: 'OrganizationPermissions', createWorkspace: boolean } } | null };

export const Sidebar_WorkspaceFragmentDoc = gql`
    fragment Sidebar_workspace on Workspace {
  slug
  ...SidebarMenu_workspace
  permissions {
    manageMembers
    update
    launchNotebookServer
  }
  shortcuts {
    id
    name
    url
    order
  }
}
    ${SidebarMenu_WorkspaceFragmentDoc}`;
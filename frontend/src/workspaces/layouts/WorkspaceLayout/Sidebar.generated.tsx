import * as Types from '../../../graphql/types';

import { gql } from '@apollo/client';
import { SidebarMenu_WorkspaceFragmentDoc } from '../../features/SidebarMenu/SidebarMenu.generated';
export type Sidebar_WorkspaceFragment = { __typename?: 'Workspace', slug: string, name: string, permissions: { __typename?: 'WorkspacePermissions', manageMembers: boolean, update: boolean, launchNotebookServer: boolean }, countries: Array<{ __typename?: 'Country', flag: string, code: string }> };

export const Sidebar_WorkspaceFragmentDoc = gql`
    fragment Sidebar_workspace on Workspace {
  slug
  ...SidebarMenu_workspace
  permissions {
    manageMembers
    update
    launchNotebookServer
  }
}
    ${SidebarMenu_WorkspaceFragmentDoc}`;
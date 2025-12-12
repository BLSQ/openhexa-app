import * as Types from '../../../graphql/types';

import { gql } from '@apollo/client';
import { Sidebar_WorkspaceFragmentDoc } from './Sidebar.generated';
export type WorkspaceLayout_WorkspaceFragment = { __typename?: 'Workspace', slug: string, name: string, permissions: { __typename?: 'WorkspacePermissions', manageMembers: boolean, update: boolean, launchNotebookServer: boolean }, shortcuts: Array<{ __typename?: 'ShortcutItem', id: string, name: string, url: string, order: number }>, countries: Array<{ __typename?: 'Country', flag: string, code: string }>, organization?: { __typename?: 'Organization', id: string, name: string, shortName?: string | null, logo?: string | null, permissions: { __typename?: 'OrganizationPermissions', createWorkspace: boolean } } | null };

export const WorkspaceLayout_WorkspaceFragmentDoc = gql`
    fragment WorkspaceLayout_workspace on Workspace {
  slug
  ...Sidebar_workspace
}
    ${Sidebar_WorkspaceFragmentDoc}`;
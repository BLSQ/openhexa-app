import * as Types from '../../../graphql/types';

import { gql } from '@apollo/client';
import { WorkspaceLayout_WorkspaceFragmentDoc } from '../WorkspaceLayout/WorkspaceLayout.generated';
export type TabLayout_WorkspaceFragment = { __typename?: 'Workspace', name: string, slug: string, assistantEnabled: boolean, permissions: { __typename?: 'WorkspacePermissions', manageMembers: boolean, update: boolean, launchNotebookServer: boolean }, shortcuts: Array<{ __typename?: 'ShortcutItem', id: string, name: string, url: string, order: number }>, countries: Array<{ __typename?: 'Country', flag: string, code: string }>, organization?: { __typename?: 'Organization', id: string, name: string, shortName?: string | null, logo?: string | null, permissions: { __typename?: 'OrganizationPermissions', createWorkspace: boolean } } | null };

export const TabLayout_WorkspaceFragmentDoc = gql`
    fragment TabLayout_workspace on Workspace {
  ...WorkspaceLayout_workspace
  name
}
    ${WorkspaceLayout_WorkspaceFragmentDoc}`;
import * as Types from '../../../graphql/types';

import { gql } from '@apollo/client';
import { WorkspaceLayout_WorkspaceFragmentDoc } from '../WorkspaceLayout/WorkspaceLayout.generated';
export type TabLayout_WorkspaceFragment = { __typename?: 'Workspace', name: string, slug: string, permissions: { __typename?: 'WorkspacePermissions', manageMembers: boolean, update: boolean, launchNotebookServer: boolean }, countries: Array<{ __typename?: 'Country', flag: string, code: string }> };

export const TabLayout_WorkspaceFragmentDoc = gql`
    fragment TabLayout_workspace on Workspace {
  ...WorkspaceLayout_workspace
  name
}
    ${WorkspaceLayout_WorkspaceFragmentDoc}`;
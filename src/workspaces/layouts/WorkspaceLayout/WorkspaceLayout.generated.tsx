import * as Types from '../../../graphql/types';

import { gql } from '@apollo/client';
import { Sidebar_WorkspaceFragmentDoc } from './Sidebar.generated';
export type WorkspaceLayout_WorkspaceFragment = { __typename?: 'Workspace', slug: string, name: string, permissions: { __typename?: 'WorkspacePermissions', manageMembers: boolean, update: boolean, launchNotebookServer: boolean }, countries: Array<{ __typename?: 'Country', flag: string, code: string }> };

export const WorkspaceLayout_WorkspaceFragmentDoc = gql`
    fragment WorkspaceLayout_workspace on Workspace {
  slug
  ...Sidebar_workspace
}
    ${Sidebar_WorkspaceFragmentDoc}`;
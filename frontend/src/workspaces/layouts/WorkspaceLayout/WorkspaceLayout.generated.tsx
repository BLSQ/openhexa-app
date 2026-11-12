import * as Types from '../../../graphql/types';

import { gql } from '@apollo/client';
import { SubscriptionBanner_OrganizationFragmentDoc } from '../../../organizations/features/SubscriptionBanner/SubscriptionBanner.generated';
import { Sidebar_WorkspaceFragmentDoc } from './Sidebar.generated';
export type WorkspaceLayout_WorkspaceFragment = { __typename?: 'Workspace', slug: string, webappsEnabled: boolean, name: string, organization: { __typename?: 'Organization', id: string, name: string, shortName?: string | null, logo?: string | null, permissions: { __typename?: 'OrganizationPermissions', manageMembers: boolean, createWorkspace: { __typename?: 'CreateWorkspacePermission', isAllowed: boolean } }, subscription?: { __typename?: 'Subscription', endDate: any, isExpired: boolean, isInGracePeriod: boolean, isExpiringSoon: boolean } | null }, permissions: { __typename?: 'WorkspacePermissions', manageMembers: boolean, update: boolean, launchNotebookServer: boolean }, shortcuts: Array<{ __typename?: 'ShortcutItem', id: string, name: string, url: string, order: number }>, countries: Array<{ __typename?: 'Country', flag: string, code: string }> };

export const WorkspaceLayout_WorkspaceFragmentDoc = gql`
    fragment WorkspaceLayout_workspace on Workspace {
  slug
  organization {
    ...SubscriptionBanner_organization
  }
  ...Sidebar_workspace
}
    ${SubscriptionBanner_OrganizationFragmentDoc}
${Sidebar_WorkspaceFragmentDoc}`;
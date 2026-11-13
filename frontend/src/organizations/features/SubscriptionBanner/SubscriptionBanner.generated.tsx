import * as Types from '../../../graphql/types';

import { gql } from '@apollo/client';
export type SubscriptionBanner_OrganizationFragment = { __typename?: 'Organization', id: string, name: string, permissions: { __typename?: 'OrganizationPermissions', manageMembers: boolean }, subscription?: { __typename?: 'Subscription', endDate: any, isExpired: boolean, isInGracePeriod: boolean, isExpiringSoon: boolean } | null };

export const SubscriptionBanner_OrganizationFragmentDoc = gql`
    fragment SubscriptionBanner_organization on Organization {
  id
  name
  permissions {
    manageMembers
  }
  subscription {
    endDate
    isExpired
    isInGracePeriod
    isExpiringSoon
  }
}
    `;
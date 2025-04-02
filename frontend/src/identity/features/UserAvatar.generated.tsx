import * as Types from '../../graphql/types';

import { gql } from '@apollo/client';
export type UserAvatar_UserFragment = { __typename?: 'User', displayName: string, avatar: { __typename?: 'Avatar', initials: string, color: string } };

export const UserAvatar_UserFragmentDoc = gql`
    fragment UserAvatar_user on User {
  displayName
  avatar {
    initials
    color
  }
}
    `;
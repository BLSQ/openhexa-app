import * as Types from '../../../graphql/types';

import { gql } from '@apollo/client';
import { UserAvatar_UserFragmentDoc } from '../../../identity/features/UserAvatar.generated';
export type User_UserFragment = { __typename?: 'User', id: string, email: string, displayName: string, avatar: { __typename?: 'Avatar', initials: string, color: string } };

export const User_UserFragmentDoc = gql`
    fragment User_user on User {
  id
  email
  displayName
  ...UserAvatar_user
}
    ${UserAvatar_UserFragmentDoc}`;
import * as Types from '../../../graphql/types';

import { gql } from '@apollo/client';
import { User_UserFragmentDoc } from '../../features/User/User.generated';
export type UserColumn_UserFragment = { __typename?: 'User', id: string, email: string, displayName: string, avatar: { __typename?: 'Avatar', initials: string, color: string } };

export const UserColumn_UserFragmentDoc = gql`
    fragment UserColumn_user on User {
  ...User_user
}
    ${User_UserFragmentDoc}`;
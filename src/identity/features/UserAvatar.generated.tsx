import * as Types from "../../graphql-types";

import { gql } from "@apollo/client";
export type UserAvatar_UserFragment = {
  __typename?: "User";
  firstName?: string | null;
  lastName?: string | null;
  avatar: { __typename?: "Avatar"; initials: string; color: string };
};

export const UserAvatar_UserFragmentDoc = gql`
  fragment UserAvatar_user on User {
    firstName
    lastName
    avatar {
      initials
      color
    }
  }
`;

import { graphql } from "graphql/gql";

export const UserAvatarUserDoc = graphql(`
fragment UserAvatar_user on User {
  displayName
  avatar {
    initials
    color
  }
}
`);

import { graphql } from "graphql/gql";

export const UserUserDoc = graphql(`
fragment User_user on User {
  id
  email
  displayName
  ...UserAvatar_user
}
`);

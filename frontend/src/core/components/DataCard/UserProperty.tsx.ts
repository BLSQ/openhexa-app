import { graphql } from "graphql/gql";

export const UserPropertyUserDoc = graphql(`
fragment UserProperty_user on User {
  ...User_user
}
`);

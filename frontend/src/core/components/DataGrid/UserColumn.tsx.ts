import { graphql } from "graphql/gql";

export const UserColumnUserDoc = graphql(`
fragment UserColumn_user on User {
  ...User_user
}
`);

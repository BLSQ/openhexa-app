import { graphql } from "graphql/gql";

export const UserPickerUserDoc = graphql(`
fragment UserPicker_user on User {
  ...User_user
}
`);

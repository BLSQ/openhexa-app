import { graphql } from "graphql/gql";

export const UpdateConnectionFieldsDialogConnectionDoc = graphql(`
fragment UpdateConnectionFieldsDialog_connection on Connection {
  id
  name
  type
  fields {
    code
    value
    secret
  }
}
`);

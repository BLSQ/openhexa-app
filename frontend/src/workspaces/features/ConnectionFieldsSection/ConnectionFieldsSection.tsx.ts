import { graphql } from "graphql/gql";

export const ConnectionFieldsSectionConnectionDoc = graphql(`
fragment ConnectionFieldsSection_connection on Connection {
  id
  type
  slug
  fields {
    code
    value
    secret
  }
  permissions {
    update
  }
  ...UpdateConnectionFieldsDialog_connection
}
`);

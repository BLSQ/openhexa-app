import { graphql } from "graphql/gql";

export const ConnectionUsageSnippetsConnectionDoc = graphql(`
fragment ConnectionUsageSnippets_connection on Connection {
  id
  type
  slug
  fields {
    code
  }
}
`);

import { graphql } from "graphql/gql";

export const WebappCardWebappDoc = graphql(`
fragment WebappCard_webapp on Webapp {
  id
  icon
  name
  workspace {
    slug
    name
  }
}
`);

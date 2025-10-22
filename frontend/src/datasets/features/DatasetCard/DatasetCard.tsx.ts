import { graphql } from "graphql/gql";

export const DatasetCardLinkDoc = graphql(`
fragment DatasetCard_link on DatasetLink {
  dataset {
    name
    slug
    description
    updatedAt
    workspace {
      slug
      name
    }
  }
  id
  workspace {
    slug
    name
  }
}
`);

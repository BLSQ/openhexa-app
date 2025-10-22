import { graphql } from "graphql/gql";

export const DatasetsPageDoc = graphql(`
fragment DatasetsPage on DatasetResultPage {
  items {
    dataset {
      id
      slug
      name
      description
      workspace {
        slug
        ...WorkspaceDisplayFragment
      }
      createdBy {
        id
        displayName
        ...UserAvatar_user
      }
      updatedAt
    }
    score
  }
  totalItems
  pageNumber
  totalPages
}
`);

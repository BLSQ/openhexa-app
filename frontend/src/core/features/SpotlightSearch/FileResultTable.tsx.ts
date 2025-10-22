import { graphql } from "graphql/gql";

export const FilesPageDoc = graphql(`
fragment FilesPage on FileResultPage {
  items {
    file {
      name
      path
      size
      updatedAt
      type
    }
    score
    workspace {
      slug
      ...WorkspaceDisplayFragment
    }
  }
  totalItems
  pageNumber
  totalPages
}
`);

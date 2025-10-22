import { graphql } from "graphql/gql";

export const DatabaseTablesPageDoc = graphql(`
fragment DatabaseTablesPage on DatabaseTableResultPage {
  items {
    databaseTable {
      name
      count
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

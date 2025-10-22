import { graphql } from "graphql/gql";

export const DatasetExplorerVersionDoc = graphql(`
fragment DatasetExplorer_version on DatasetVersion {
  id
  files(page: $page, perPage: $perPage) {
    totalPages
    pageNumber
    totalItems
    items {
      ...DatasetExplorer_file
    }
  }
  ...DatasetVersionFileSample_version
  ...DatasetVersionFileColumns_version
}
`);

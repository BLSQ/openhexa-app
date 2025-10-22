import { graphql } from "graphql/gql";

export const DatasetExplorerFileDoc = graphql(`
fragment DatasetExplorer_file on DatasetVersionFile {
  id
  filename
  createdAt
  createdBy {
    displayName
  }
  ...DownloadVersionFile_file
  ...DatasetVersionFileSample_file
  ...DatasetVersionFileColumns_file
  contentType
  size
  uri
}
`);

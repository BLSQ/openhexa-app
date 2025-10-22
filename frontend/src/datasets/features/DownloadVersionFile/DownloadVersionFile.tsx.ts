import { graphql } from "graphql/gql";

export const DownloadVersionFileFileDoc = graphql(`
fragment DownloadVersionFile_file on DatasetVersionFile {
  id
  filename
}
`);

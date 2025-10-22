import { graphql } from "graphql/gql";

export const DatasetVersionFilesDataGridVersionDoc = graphql(`
fragment DatasetVersionFilesDataGrid_version on DatasetVersion {
  id
  name
  permissions {
    download
  }
}
`);

import { graphql } from "graphql/gql";

export const DatasetVersionFileColumnsFileDoc = graphql(`
fragment DatasetVersionFileColumns_file on DatasetVersionFile {
  id
  filename
  ...ColumnMetadataDrawer_file
}
`);

export const DatasetVersionFileColumnsVersionDoc = graphql(`
fragment DatasetVersionFileColumns_version on DatasetVersion {
  name
  dataset {
    slug
    permissions {
      update
    }
    workspace {
      slug
    }
  }
}
`);

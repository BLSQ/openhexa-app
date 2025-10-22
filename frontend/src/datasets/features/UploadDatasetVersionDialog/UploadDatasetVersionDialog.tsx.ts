import { graphql } from "graphql/gql";

export const UploadDatasetVersionDialogDatasetLinkDoc = graphql(`
fragment UploadDatasetVersionDialog_datasetLink on DatasetLink {
  id
  dataset {
    id
    name
    slug
    workspace {
      slug
    }
  }
  workspace {
    slug
  }
}
`);

import { graphql } from "graphql/gql";

export const DatasetVersionFileSampleFileDoc = graphql(`
fragment DatasetVersionFileSample_file on DatasetVersionFile {
  id
  filename
  contentType
  size
  downloadUrl(attachment: false)
}
`);

export const DatasetVersionFileSampleVersionDoc = graphql(`
fragment DatasetVersionFileSample_version on DatasetVersion {
  name
  dataset {
    slug
    workspace {
      slug
    }
  }
}
`);

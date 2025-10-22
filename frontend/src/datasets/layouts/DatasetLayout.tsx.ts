import { graphql } from "graphql/gql";

export const DatasetLayoutWorkspaceDoc = graphql(`
fragment DatasetLayout_workspace on Workspace {
  ...WorkspaceLayout_workspace
  name
  slug
}
`);

export const DatasetLayoutDatasetLinkDoc = graphql(`
fragment DatasetLayout_datasetLink on DatasetLink {
  ...UploadDatasetVersionDialog_datasetLink
  ...PinDatasetButton_link
  dataset {
    workspace {
      slug
    }
    slug
    permissions {
      delete
      createVersion
    }
  }
}
`);

export const DatasetLayoutVersionDoc = graphql(`
fragment DatasetLayout_version on DatasetVersion {
  id
  name
  ...DatasetVersionPicker_version
}
`);

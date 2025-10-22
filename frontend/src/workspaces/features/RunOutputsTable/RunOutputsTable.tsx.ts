import { graphql } from "graphql/gql";

export const RunOutputsTableWorkspaceDoc = graphql(`
fragment RunOutputsTable_workspace on Workspace {
  ...DownloadBucketObject_workspace
  slug
  bucket {
    name
  }
}
`);

export const RunOutputsTableRunDoc = graphql(`
fragment RunOutputsTable_run on PipelineRun {
  id
  outputs {
    __typename
    ... on GenericOutput {
      genericName: name
      genericType: type
      genericUri: uri
    }
    ... on BucketObject {
      name
      key
      path
      type
    }
    ... on DatabaseTable {
      tableName: name
    }
  }
  datasetVersions {
    name
    dataset {
      slug
      name
      workspace {
        slug
      }
    }
  }
}
`);

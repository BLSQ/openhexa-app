import { graphql } from "graphql/gql";

export const BucketExplorerWorkspaceDoc = graphql(`
fragment BucketExplorer_workspace on Workspace {
  slug
  ...DownloadBucketObject_workspace
  ...DeleteBucketObject_workspace
}
`);

export const BucketExplorerObjectsDoc = graphql(`
fragment BucketExplorer_objects on BucketObjectPage {
  hasNextPage
  hasPreviousPage
  pageNumber
  items {
    key
    name
    path
    size
    updatedAt
    type
    ...DownloadBucketObject_object
    ...DeleteBucketObject_object
  }
}
`);

import { graphql } from "graphql/gql";

export const DownloadBucketObjectWorkspaceDoc = graphql(`
fragment DownloadBucketObject_workspace on Workspace {
  slug
}
`);

export const DownloadBucketObjectObjectDoc = graphql(`
fragment DownloadBucketObject_object on BucketObject {
  key
}
`);

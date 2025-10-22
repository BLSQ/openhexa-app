import { graphql } from "graphql/gql";

export const FileBrowserDialogBucketObjectDoc = graphql(`
fragment FileBrowserDialog_bucketObject on BucketObject {
  key
  name
  path
  size
  updatedAt
  type
}
`);

import { graphql } from "graphql/gql";

export const DeleteBucketObjectWorkspaceDoc = graphql(`
fragment DeleteBucketObject_workspace on Workspace {
  slug
  permissions {
    deleteObject
  }
}
`);

export const DeleteBucketObjectObjectDoc = graphql(`
fragment DeleteBucketObject_object on BucketObject {
  key
  name
  type
}
`);

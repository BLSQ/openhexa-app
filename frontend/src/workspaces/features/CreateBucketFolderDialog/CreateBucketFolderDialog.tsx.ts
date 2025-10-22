import { graphql } from "graphql/gql";

export const CreateBucketFolderDialogWorkspaceDoc = graphql(`
fragment CreateBucketFolderDialog_workspace on Workspace {
  slug
  permissions {
    createObject
  }
  bucket {
    name
  }
}
`);

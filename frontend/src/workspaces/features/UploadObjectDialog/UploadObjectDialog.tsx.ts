import { graphql } from "graphql/gql";

export const UploadObjectDialogWorkspaceDoc = graphql(`
fragment UploadObjectDialog_workspace on Workspace {
  slug
  permissions {
    createObject
  }
}
`);

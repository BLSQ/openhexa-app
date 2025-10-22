import { graphql } from "graphql/gql";

export const CreateDatasetDialogWorkspaceDoc = graphql(`
fragment CreateDatasetDialog_workspace on Workspace {
  slug
  name
  permissions {
    createDataset
  }
}
`);

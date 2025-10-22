import { graphql } from "graphql/gql";

export const GenerateWorkspaceDatabasePasswordDialogWorkspaceDoc = graphql(`
fragment GenerateWorkspaceDatabasePasswordDialog_workspace on Workspace {
  slug
}
`);

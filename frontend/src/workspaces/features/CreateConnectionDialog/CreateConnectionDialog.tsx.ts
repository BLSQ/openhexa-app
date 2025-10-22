import { graphql } from "graphql/gql";

export const CreateConnectionDialogWorkspaceDoc = graphql(`
fragment CreateConnectionDialog_workspace on Workspace {
  slug
}
`);

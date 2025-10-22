import { graphql } from "graphql/gql";

export const DatabaseVariablesSectionWorkspaceDoc = graphql(`
fragment DatabaseVariablesSection_workspace on Workspace {
  slug
  database {
    credentials {
      dbName
      username
      password
      host
      port
      url
    }
  }
}
`);

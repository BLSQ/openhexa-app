import { graphql } from "graphql/gql";

export const DatabaseTableDeleteTriggerWorkspaceDoc = graphql(`
fragment DatabaseTableDeleteTrigger_workspace on Workspace {
  slug
  permissions {
    deleteDatabaseTable
  }
}
`);

export const DatabaseTableDeleteTriggerDatabaseDoc = graphql(`
fragment DatabaseTableDeleteTrigger_database on DatabaseTable {
  name
}
`);

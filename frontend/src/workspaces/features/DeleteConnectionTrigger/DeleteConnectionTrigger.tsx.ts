import { graphql } from "graphql/gql";

export const DeleteConnectionTriggerWorkspaceDoc = graphql(`
fragment DeleteConnectionTrigger_workspace on Workspace {
  slug
}
`);

export const DeleteConnectionTriggerConnectionDoc = graphql(`
fragment DeleteConnectionTrigger_connection on Connection {
  id
  name
  permissions {
    delete
  }
}
`);

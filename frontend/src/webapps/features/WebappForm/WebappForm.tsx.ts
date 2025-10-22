import { graphql } from "graphql/gql";

export const WebappFormWebappDoc = graphql(`
fragment WebappForm_webapp on Webapp {
  id
  name
  description
  url
  icon
  permissions {
    update
    delete
  }
}
`);

export const WebappFormWorkspaceDoc = graphql(`
fragment WebappForm_workspace on Workspace {
  ...WorkspaceLayout_workspace
}
`);

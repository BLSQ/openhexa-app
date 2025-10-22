import { graphql } from "graphql/gql";

export const WebappDeleteWebappDoc = graphql(`
fragment WebappDelete_webapp on Webapp {
  id
  name
}
`);

export const WebappDeleteWorkspaceDoc = graphql(`
fragment WebappDelete_workspace on Workspace {
  slug
}
`);

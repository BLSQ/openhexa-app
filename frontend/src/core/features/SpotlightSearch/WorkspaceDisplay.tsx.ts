import { graphql } from "graphql/gql";

export const WorkspaceDisplayFragmentDoc = graphql(`
fragment WorkspaceDisplayFragment on Workspace {
  name
  countries {
    code
  }
}
`);

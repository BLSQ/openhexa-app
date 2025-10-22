import { graphql } from "graphql/gql";

export const SidebarMenuWorkspaceDoc = graphql(`
fragment SidebarMenu_workspace on Workspace {
  slug
  name
  countries {
    flag
    code
  }
  organization {
    id
    name
    shortName
    permissions {
      createWorkspace
    }
  }
}
`);

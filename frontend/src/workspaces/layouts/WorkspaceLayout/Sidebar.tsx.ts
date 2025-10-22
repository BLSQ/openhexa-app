import { graphql } from "graphql/gql";

export const SidebarWorkspaceDoc = graphql(`
fragment Sidebar_workspace on Workspace {
  slug
  ...SidebarMenu_workspace
  permissions {
    manageMembers
    update
    launchNotebookServer
  }
}
`);

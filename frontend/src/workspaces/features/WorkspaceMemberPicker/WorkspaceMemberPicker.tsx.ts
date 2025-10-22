import { graphql } from "graphql/gql";

export const WorkspaceMemberPickerWorkspaceDoc = graphql(`
fragment WorkspaceMemberPicker_workspace on Workspace {
  slug
  members {
    items {
      id
      user {
        id
        displayName
      }
    }
  }
}
`);

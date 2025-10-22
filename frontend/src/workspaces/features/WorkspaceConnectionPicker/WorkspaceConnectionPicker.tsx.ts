import { graphql } from "graphql/gql";

export const WorkspaceConnectionPickerWorkspaceDoc = graphql(`
fragment WorkspaceConnectionPicker_workspace on Workspace {
  slug
  connections {
    id
    name
    slug
    type
  }
}
`);

import { graphql } from "graphql/gql";

export const WorkspacePickerValueDoc = graphql(`
fragment WorkspacePicker_value on Workspace {
  slug
  name
}
`);

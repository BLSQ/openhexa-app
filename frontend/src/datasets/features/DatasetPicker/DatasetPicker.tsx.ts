import { graphql } from "graphql/gql";

export const DatasetPickerWorkspaceDoc = graphql(`
fragment DatasetPicker_workspace on Workspace {
  datasets {
    items {
      id
      dataset {
        slug
        name
      }
    }
  }
}
`);

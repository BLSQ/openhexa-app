import { graphql } from "graphql/gql";

export const BucketObjectPickerWorkspaceDoc = graphql(`
fragment BucketObjectPicker_workspace on Workspace {
  slug
}
`);

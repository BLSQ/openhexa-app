import { graphql } from "graphql/gql";

export const CreatePipelineDialogWorkspaceDoc = graphql(`
fragment CreatePipelineDialog_workspace on Workspace {
  slug
  ...BucketObjectPicker_workspace
}
`);

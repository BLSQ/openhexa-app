import { graphql } from "graphql/gql";

export const UpgradePipelineFromTemplateDialogPipelineDoc = graphql(`
fragment UpgradePipelineFromTemplateDialog_pipeline on Pipeline {
  id
  code
  newTemplateVersions {
    id
    versionNumber
    changelog
    createdAt
  }
}
`);

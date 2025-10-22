import { graphql } from "graphql/gql";

export const DeleteTemplateVersionTriggerVersionDoc = graphql(`
fragment DeleteTemplateVersionTrigger_version on PipelineTemplateVersion {
  id
  versionNumber
  template {
    id
  }
  permissions {
    delete
  }
}
`);

import { graphql } from "graphql/gql";

export const TemplateVersionCardVersionDoc = graphql(`
fragment TemplateVersionCard_version on PipelineTemplateVersion {
  id
  versionNumber
  changelog
  createdAt
  isLatestVersion
  user {
    displayName
  }
  permissions {
    update
  }
  template {
    id
    code
  }
  ...DeleteTemplateVersionTrigger_version
}
`);

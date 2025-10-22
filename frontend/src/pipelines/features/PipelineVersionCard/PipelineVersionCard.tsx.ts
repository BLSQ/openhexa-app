import { graphql } from "graphql/gql";

export const PipelineVersionCardVersionDoc = graphql(`
fragment PipelineVersionCard_version on PipelineVersion {
  id
  versionName
  name
  description
  externalLink
  isLatestVersion
  createdAt
  user {
    displayName
  }
  permissions {
    update
  }
  parameters {
    ...ParameterField_parameter
  }
  pipeline {
    id
    code
  }
  templateVersion {
    id
    versionNumber
    template {
      id
      name
    }
  }
  ...DownloadPipelineVersion_version
  ...DeletePipelineVersionTrigger_version
}
`);

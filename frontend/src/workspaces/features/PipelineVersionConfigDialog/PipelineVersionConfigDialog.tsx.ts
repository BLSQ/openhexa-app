import { graphql } from "graphql/gql";

export const PipelineVersionConfigDialogVersionDoc = graphql(`
fragment PipelineVersionConfigDialog_version on PipelineVersion {
  id
  name
  description
  externalLink
  isLatestVersion
  createdAt
  config
  pipeline {
    id
    schedule
    workspace {
      slug
    }
  }
  parameters {
    ...ParameterField_parameter
  }
}
`);

import { graphql } from "graphql/gql";

export const PipelineVersionPickerPipelineDoc = graphql(`
fragment PipelineVersionPicker_pipeline on Pipeline {
  id
}
`);

export const PipelineVersionPickerVersionDoc = graphql(`
fragment PipelineVersionPicker_version on PipelineVersion {
  id
  versionName
  createdAt
  config
  parameters {
    ...ParameterField_parameter
  }
  user {
    displayName
  }
}
`);

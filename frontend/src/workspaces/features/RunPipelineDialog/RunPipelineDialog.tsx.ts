import { graphql } from "graphql/gql";

export const RunPipelineDialogVersionDoc = graphql(`
fragment RunPipelineDialog_version on PipelineVersion {
  id
  versionName
  createdAt
  config
  user {
    displayName
  }
  parameters {
    ...ParameterField_parameter
  }
}
`);

export const RunPipelineDialogPipelineDoc = graphql(`
fragment RunPipelineDialog_pipeline on Pipeline {
  id
  workspace {
    slug
  }
  permissions {
    run
  }
  code
  type
  currentVersion {
    id
  }
  ...PipelineVersionPicker_pipeline
}
`);

export const RunPipelineDialogRunDoc = graphql(`
fragment RunPipelineDialog_run on PipelineRun {
  id
  config
  version {
    id
    versionName
    createdAt
    parameters {
      ...ParameterField_parameter
    }
    user {
      displayName
    }
  }
}
`);

import { graphql } from "graphql/gql";

export const PipelineLayoutWorkspaceDoc = graphql(`
fragment PipelineLayout_workspace on Workspace {
  ...TabLayout_workspace
}
`);

export const PipelineLayoutPipelineDoc = graphql(`
fragment PipelineLayout_pipeline on Pipeline {
  id
  code
  name
  permissions {
    run
    delete
    update
    createTemplateVersion {
      isAllowed
      reasons
    }
  }
  template {
    id
    name
    code
  }
  currentVersion {
    id
    name
    description
    config
    externalLink
    templateVersion {
      id
    }
    ...PipelineVersionPicker_version
    ...DownloadPipelineVersion_version
  }
  ...RunPipelineDialog_pipeline
}
`);

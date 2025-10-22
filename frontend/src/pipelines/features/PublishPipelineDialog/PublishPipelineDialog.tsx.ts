import { graphql } from "graphql/gql";

export const PipelinePublishPipelineDoc = graphql(`
fragment PipelinePublish_pipeline on Pipeline {
  id
  name
  description
  currentVersion {
    id
    versionName
  }
  template {
    id
    name
  }
}
`);

export const PipelinePublishWorkspaceDoc = graphql(`
fragment PipelinePublish_workspace on Workspace {
  slug
}
`);

import { graphql } from "graphql/gql";

export const PipelineCardPipelineDoc = graphql(`
fragment PipelineCard_pipeline on Pipeline {
  id
  code
  name
  schedule
  description
  type
  sourceTemplate {
    id
    name
  }
  ...PipelineMetadataDisplay_pipeline
  currentVersion {
    user {
      ...User_user
    }
    versionName
    createdAt
  }
  lastRuns: runs(orderBy: EXECUTION_DATE_DESC, page: 1, perPage: 1) {
    items {
      ...PipelineRunStatusBadge_run
      executionDate
      user {
        ...User_user
      }
    }
  }
}
`);

export const PipelineCardWorkspaceDoc = graphql(`
fragment PipelineCard_workspace on Workspace {
  slug
}
`);

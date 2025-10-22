import { graphql } from "graphql/gql";

export const PipelineTemplatesPageDoc = graphql(`
fragment PipelineTemplatesPage on PipelineTemplateResultPage {
  items {
    pipelineTemplate {
      id
      code
      name
      description
      workspace {
        slug
        ...WorkspaceDisplayFragment
      }
      currentVersion {
        id
        versionNumber
      }
      updatedAt
    }
    score
  }
  totalItems
  pageNumber
  totalPages
}
`);

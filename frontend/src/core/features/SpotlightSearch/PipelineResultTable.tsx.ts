import { graphql } from "graphql/gql";

export const PipelinesPageDoc = graphql(`
fragment PipelinesPage on PipelineResultPage {
  items {
    pipeline {
      id
      code
      name
      description
      updatedAt
      functionalType
      tags {
        ...Tag_tag
      }
      workspace {
        slug
        ...WorkspaceDisplayFragment
      }
      lastRuns: runs(orderBy: EXECUTION_DATE_DESC, page: 1, perPage: 1) {
        items {
          ...PipelineRunStatusBadge_run
        }
      }
    }
    score
  }
  totalItems
  pageNumber
  totalPages
}
`);

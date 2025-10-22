import { graphql } from "graphql/gql";

export const PipelineRunFavoriteIconRunDoc = graphql(`
fragment PipelineRunFavoriteIcon_run on DAGRun {
  isFavorite
}
`);

import { graphql } from "graphql/gql";

export const PipelineRunFavoriteTriggerRunDoc = graphql(`
fragment PipelineRunFavoriteTrigger_run on DAGRun {
  id
  label
  isFavorite
  ...PipelineRunFavoriteIcon_run
}
`);

import { graphql } from "graphql/gql";

export const PipelineRunStatusBadgeRunDoc = graphql(`
fragment PipelineRunStatusBadge_run on PipelineRun {
  id
  status
  ...usePipelineRunPoller_run
}
`);

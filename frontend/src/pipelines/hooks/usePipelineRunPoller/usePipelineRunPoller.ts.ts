import { graphql } from "graphql/gql";

export const UsePipelineRunPollerRunDoc = graphql(`
fragment usePipelineRunPoller_run on PipelineRun {
  id
  status
}
`);

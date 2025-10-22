import { graphql } from "graphql/gql";

export const NewRunDoc = graphql(`
fragment NewRun on PipelineRun {
  id
}
`);

import { graphql } from "graphql/gql";

export const PipelineRunOutputEntryOutputDoc = graphql(`
fragment PipelineRunOutputEntry_output on DAGRunOutput {
  title
  uri
}
`);

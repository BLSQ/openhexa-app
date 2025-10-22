import { graphql } from "graphql/gql";

export const PipelinesPickerValueDoc = graphql(`
fragment PipelinesPicker_value on DAG {
  id
  externalId
}
`);

import { graphql } from "graphql/gql";

export const PipelineRunFormDagDoc = graphql(`
fragment PipelineRunForm_dag on DAG {
  template {
    sampleConfig
  }
  formCode
  id
}
`);

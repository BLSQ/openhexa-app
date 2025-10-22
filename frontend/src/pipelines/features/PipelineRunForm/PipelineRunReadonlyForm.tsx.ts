import { graphql } from "graphql/gql";

export const PipelineRunReadonlyFormDagDoc = graphql(`
fragment PipelineRunReadonlyForm_dag on DAG {
  formCode
  id
}
`);

export const PipelineRunReadonlyFormDagRunDoc = graphql(`
fragment PipelineRunReadonlyForm_dagRun on DAGRun {
  config
}
`);

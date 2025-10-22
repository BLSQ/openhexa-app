import { graphql } from "graphql/gql";

export const PipelineRunDataCardDagDoc = graphql(`
fragment PipelineRunDataCard_dag on DAG {
  id
  externalId
  label
  ...PipelineRunReadonlyForm_dag
}
`);

export const PipelineRunDataCardDagRunDoc = graphql(`
fragment PipelineRunDataCard_dagRun on DAGRun {
  id
  label
  externalId
  externalUrl
  executionDate
  triggerMode
  status
  config
  duration
  outputs {
    ...PipelineRunOutputEntry_output
  }
  user {
    displayName
    ...UserProperty_user
  }
  progress
  messages {
    __typename
  }
  ...RunMessages_dagRun
  ...RunLogs_dagRun
  ...PipelineRunReadonlyForm_dagRun
  ...PipelineRunFavoriteTrigger_run
}
`);

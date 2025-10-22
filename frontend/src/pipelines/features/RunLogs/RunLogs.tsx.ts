import { graphql } from "graphql/gql";

export const RunLogsDagRunDoc = graphql(`
fragment RunLogs_dagRun on DAGRun {
  id
  logs
  status
}
`);

export const RunLogsRunDoc = graphql(`
fragment RunLogs_run on PipelineRun {
  id
  logs
  status
}
`);

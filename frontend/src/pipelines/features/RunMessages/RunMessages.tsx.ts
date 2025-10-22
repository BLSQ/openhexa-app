import { graphql } from "graphql/gql";

export const RunMessagesDagRunDoc = graphql(`
fragment RunMessages_dagRun on DAGRun {
  id
  status
  messages {
    message
    timestamp
    priority
  }
}
`);

export const RunMessagesRunDoc = graphql(`
fragment RunMessages_run on PipelineRun {
  id
  status
  messages {
    message
    timestamp
    priority
  }
}
`);

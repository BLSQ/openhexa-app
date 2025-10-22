import { graphql } from "graphql/gql";

export const DeletePipelineVersionTriggerVersionDoc = graphql(`
fragment DeletePipelineVersionTrigger_version on PipelineVersion {
  id
  name
  pipeline {
    id
  }
  permissions {
    delete
  }
}
`);

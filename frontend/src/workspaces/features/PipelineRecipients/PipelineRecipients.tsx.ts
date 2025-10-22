import { graphql } from "graphql/gql";

export const PipelineRecipientsPipelineDoc = graphql(`
fragment PipelineRecipients_pipeline on Pipeline {
  id
  code
  permissions {
    update
  }
}
`);

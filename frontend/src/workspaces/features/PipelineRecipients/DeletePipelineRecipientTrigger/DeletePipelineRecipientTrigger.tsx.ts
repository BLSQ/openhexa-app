import { graphql } from "graphql/gql";

export const DeletePipelineRecipientTriggerRecipientDoc = graphql(`
fragment DeletePipelineRecipientTrigger_recipient on PipelineRecipient {
  id
  user {
    displayName
  }
}
`);

export const DeletePipelineRecipientTriggerPipelineDoc = graphql(`
fragment DeletePipelineRecipientTrigger_pipeline on Pipeline {
  permissions {
    update
  }
}
`);

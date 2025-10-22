import { graphql } from "graphql/gql";

export const GeneratePipelineWebhookUrlDialogPipelineDoc = graphql(`
fragment GeneratePipelineWebhookUrlDialog_pipeline on Pipeline {
  id
  code
}
`);

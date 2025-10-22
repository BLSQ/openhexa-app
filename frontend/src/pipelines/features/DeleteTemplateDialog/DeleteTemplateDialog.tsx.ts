import { graphql } from "graphql/gql";

export const PipelineTemplateDialogPipelineTemplateDoc = graphql(`
fragment PipelineTemplateDialog_pipelineTemplate on PipelineTemplate {
  id
  name
}
`);

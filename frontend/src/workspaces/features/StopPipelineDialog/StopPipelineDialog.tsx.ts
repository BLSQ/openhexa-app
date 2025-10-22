import { graphql } from "graphql/gql";

export const StopPipelineDialogRunDoc = graphql(`
fragment StopPipelineDialog_run on PipelineRun {
  id
}
`);

export const StopPipelineDialogPipelineDoc = graphql(`
fragment StopPipelineDialog_pipeline on Pipeline {
  code
}
`);

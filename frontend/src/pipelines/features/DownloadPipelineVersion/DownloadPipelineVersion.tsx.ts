import { graphql } from "graphql/gql";

export const DownloadPipelineVersionVersionDoc = graphql(`
fragment DownloadPipelineVersion_version on PipelineVersion {
  id
  name
  pipeline {
    id
    code
  }
}
`);

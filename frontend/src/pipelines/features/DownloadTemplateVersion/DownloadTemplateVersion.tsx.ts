import { graphql } from "graphql/gql";

export const DownloadTemplateVersionVersionDoc = graphql(`
fragment DownloadTemplateVersion_version on PipelineTemplateVersion {
  id
}
`);

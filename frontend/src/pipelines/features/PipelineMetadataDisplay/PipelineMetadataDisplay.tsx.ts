import { graphql } from "graphql/gql";

export const PipelineMetadataDisplayPipelineDoc = graphql(`
fragment PipelineMetadataDisplay_pipeline on Pipeline {
  functionalType
  tags {
    ...Tag_tag
  }
}
`);

export const PipelineMetadataDisplayTemplateDoc = graphql(`
fragment PipelineMetadataDisplay_template on PipelineTemplate {
  functionalType
  tags {
    ...Tag_tag
  }
}
`);

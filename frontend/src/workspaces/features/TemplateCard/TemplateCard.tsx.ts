import { graphql } from "graphql/gql";

export const TemplateCardTemplateDoc = graphql(`
fragment TemplateCard_template on PipelineTemplate {
  id
  code
  name
  description
  ...PipelineMetadataDisplay_template
  currentVersion {
    id
    createdAt
    user {
      ...User_user
    }
  }
}
`);

export const TemplateCardWorkspaceDoc = graphql(`
fragment TemplateCard_workspace on Workspace {
  slug
}
`);

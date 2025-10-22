import { graphql } from "graphql/gql";

export const TemplateLayoutWorkspaceDoc = graphql(`
fragment TemplateLayout_workspace on Workspace {
  ...TabLayout_workspace
}
`);

export const TemplateLayoutTemplateDoc = graphql(`
fragment TemplateLayout_template on PipelineTemplate {
  id
  code
  name
  permissions {
    delete
    update
  }
  currentVersion {
    id
    ...DownloadTemplateVersion_version
  }
}
`);

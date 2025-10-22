import Page from "core/components/Page";
import { createGetServerSideProps } from "core/helpers/page";
import { NextPageWithLayout } from "core/helpers/types";
import { FilesEditor } from "workspaces/features/FilesEditor";
import TemplateLayout from "workspaces/layouts/TemplateLayout";
import DataCard from "core/components/DataCard";
import Spinner from "core/components/Spinner";
import { createTemplatePageServerSideProps } from "workspaces/helpers/templatePages";
import { useQuery } from "@apollo/client/react";
import { graphql } from "graphql/gql";

const WorkspaceTemplatePageDoc = graphql(`
query WorkspaceTemplatePage($workspaceSlug: String!, $templateCode: String!) {
  workspace(slug: $workspaceSlug) {
    slug
    name
    ...PipelineLayout_workspace
  }
  template: templateByCode(code: $templateCode) {
    ...TemplateLayout_template
    permissions {
      update
      delete
    }
    id
    code
    name
    description
    functionalType
    tags {
      ...Tag_tag
    }
    currentVersion {
      id
      versionNumber
      sourcePipelineVersion {
        files {
          ...FilesEditor_file
        }
        zipfile
      }
    }
  }
}
`);

type WorkspaceTemplateCodePageProps = {
  templateCode: string;
  workspaceSlug: string;
};

const WorkspaceTemplateCodePage: NextPageWithLayout = (
  props: WorkspaceTemplateCodePageProps,
) => {
  const { templateCode, workspaceSlug } = props;

  const { data, loading } = useQuery(WorkspaceTemplatePageDoc, {
    variables: {
      workspaceSlug,
      templateCode,
    },
  });

  if (!data?.workspace || !data?.template) {
    return null;
  }

  const { workspace, template } = data;

  if (!template.currentVersion) {
    return null;
  }

  return (
    <Page title={template.name}>
      <TemplateLayout
        workspace={workspace}
        template={template}
        currentTab="code"
      >
        <DataCard.FormSection>
          <div className="relative overflow-hidden">
            {loading && (
              <div className="absolute inset-0 backdrop-blur-xs flex justify-center items-center z-10">
                <Spinner size="md" />
              </div>
            )}
            <div className="w-full overflow-x-auto">
              <FilesEditor
                name={template.name}
                files={template.currentVersion.sourcePipelineVersion.files}
              />
            </div>
          </div>
        </DataCard.FormSection>
      </TemplateLayout>
    </Page>
  );
};

WorkspaceTemplateCodePage.getLayout = (page) => page;

export const getServerSideProps = createGetServerSideProps({
  requireAuth: true,
  async getServerSideProps(ctx, client) {
    await FilesEditor.prefetch(ctx, client);

    const originalProps = createTemplatePageServerSideProps();
    return await originalProps.getServerSideProps(ctx, client);
  },
});

export default WorkspaceTemplateCodePage;

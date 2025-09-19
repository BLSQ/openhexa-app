import Page from "core/components/Page";
import { createGetServerSideProps } from "core/helpers/page";
import { NextPageWithLayout } from "core/helpers/types";
import { FilesEditor } from "workspaces/features/FilesEditor";
import { useWorkspaceTemplatePageQuery } from "workspaces/graphql/queries.generated";
import TemplateLayout from "workspaces/layouts/TemplateLayout";
import DataCard from "core/components/DataCard";
import Spinner from "core/components/Spinner";
import { createTemplatePageServerSideProps } from "workspaces/helpers/templatePages";

type WorkspaceTemplateCodePageProps = {
  templateCode: string;
  workspaceSlug: string;
};

const WorkspaceTemplateCodePage: NextPageWithLayout = (
  props: WorkspaceTemplateCodePageProps,
) => {
  const { templateCode, workspaceSlug } = props;

  const { data, loading } = useWorkspaceTemplatePageQuery({
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

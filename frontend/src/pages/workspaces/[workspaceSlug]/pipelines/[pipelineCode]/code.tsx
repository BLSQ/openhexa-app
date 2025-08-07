import Page from "core/components/Page";
import { createGetServerSideProps } from "core/helpers/page";
import { NextPageWithLayout } from "core/helpers/types";
import { useTranslation } from "next-i18next";
import { FilesEditor } from "workspaces/features/FilesEditor";
import {
  useGetPipelineVersionFilesLazyQuery,
  useWorkspacePipelineCodePageQuery,
  WorkspacePipelineCodePageDocument,
  WorkspacePipelineCodePageQuery,
  WorkspacePipelineCodePageQueryVariables,
} from "workspaces/graphql/queries.generated";
import PipelineLayout from "workspaces/layouts/PipelineLayout";
import DataCard from "core/components/DataCard";
import PipelineVersionPicker from "workspaces/features/PipelineVersionPicker";
import { useState } from "react";
import { PipelineVersionPicker_VersionFragment } from "workspaces/features/PipelineVersionPicker/PipelineVersionPicker.generated";
import Spinner from "core/components/Spinner";

type Props = {
  pipelineCode: string;
  workspaceSlug: string;
};

const WorkspacePipelineCodePage: NextPageWithLayout = (props: Props) => {
  const { pipelineCode, workspaceSlug } = props;
  const { t } = useTranslation();
  const [selectedVersion, setSelectedVersion] =
    useState<PipelineVersionPicker_VersionFragment | null>(null);

  const { data, loading } = useWorkspacePipelineCodePageQuery({
    variables: {
      workspaceSlug,
      pipelineCode,
    },
  });
  const [fetchPipelineVersion, { data: versionData, loading: versionLoading }] =
    useGetPipelineVersionFilesLazyQuery();

  if (!data?.workspace || !data?.pipeline) {
    return null;
  }
  const { workspace, pipeline } = data;

  if (!pipeline.currentVersion) {
    return null;
  }
  const onVersionChange = (version: PipelineVersionPicker_VersionFragment) => {
    if (version) {
      setSelectedVersion(version);
      fetchPipelineVersion({
        variables: {
          versionId: version.id,
        },
      }).then();
    }
  };

  const handleVersionCreated = (version: PipelineVersionPicker_VersionFragment) => {
    if (version) {
      setSelectedVersion(version);
      fetchPipelineVersion({
        variables: {
          versionId: version.id,
        },
      }).then();
    }
  };

  const versionToShow = versionData?.pipelineVersion ?? pipeline.currentVersion;
  return (
    <Page title={pipeline.name ?? t("Pipeline Code")}>
      <PipelineLayout
        workspace={workspace}
        pipeline={pipeline}
        currentTab="code"
      >
        <DataCard.FormSection>
          <div className="flex items-center gap-3">
            <label className="text-md font-medium text-gray-700">
              {t("Version")}:
            </label>
            <div className="w-70">
              <PipelineVersionPicker
                required
                value={selectedVersion ?? pipeline.currentVersion}
                pipeline={pipeline}
                onChange={onVersionChange}
              />
            </div>
          </div>
          <div className="relative">
            {(loading || versionLoading) && (
              <div className="absolute inset-0 backdrop-blur-xs flex justify-center items-center z-10">
                <Spinner size="md" />
              </div>
            )}
            <FilesEditor
              key={versionToShow.id}
              name={versionToShow.versionName}
              files={versionToShow.files}
              isEditable={true}
              workspaceSlug={workspaceSlug}
              pipelineCode={pipelineCode}
              pipelineId={pipeline.id}
              onVersionCreated={handleVersionCreated}
            />
          </div>
        </DataCard.FormSection>
      </PipelineLayout>
    </Page>
  );
};

WorkspacePipelineCodePage.getLayout = (page) => page;

export const getServerSideProps = createGetServerSideProps({
  requireAuth: true,
  async getServerSideProps(ctx, client) {
    await PipelineLayout.prefetch(ctx, client);
    await FilesEditor.prefetch(ctx, client);

    const { data } = await client.query<
      WorkspacePipelineCodePageQuery,
      WorkspacePipelineCodePageQueryVariables
    >({
      query: WorkspacePipelineCodePageDocument,
      variables: {
        workspaceSlug: ctx.params!.workspaceSlug as string,
        pipelineCode: ctx.params!.pipelineCode as string,
      },
    });

    if (!data.workspace || !data.pipeline) {
      return { notFound: true };
    }

    return {
      props: {
        workspaceSlug: ctx.params!.workspaceSlug,
        pipelineCode: ctx.params!.pipelineCode,
      },
    };
  },
});

export default WorkspacePipelineCodePage;

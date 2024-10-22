import Page from "core/components/Page";
import { createGetServerSideProps } from "core/helpers/page";
import { NextPageWithLayout } from "core/helpers/types";
import DatasetExplorer from "datasets/features/DatasetExplorer";
import LinkDatasetDialog from "datasets/features/LinkDatasetDialog";
import DatasetLayout from "datasets/layouts/DatasetLayout";
import { useTranslation } from "next-i18next";
import { useRouter } from "next/router";
import { useState } from "react";
import {
  useWorkspaceDatasetFilesPageQuery,
  WorkspaceDatasetFilesPageDocument,
  WorkspaceDatasetFilesPageQuery,
  WorkspaceDatasetFilesPageQueryVariables,
} from "workspaces/graphql/queries.generated";

export type WorkspaceDatasetFilesPageProps = {
  isSpecificVersion: boolean;
  workspaceSlug: string;
  datasetSlug: string;
  versionId: string;
  fileId: string | null;
};

const WorkspaceDatasetFilesPage: NextPageWithLayout = (
  props: WorkspaceDatasetFilesPageProps,
) => {
  const { t } = useTranslation();
  const router = useRouter();
  const [isLinkDialogOpen, setLinkDialogOpen] = useState(false);
  const { fileId, isSpecificVersion, workspaceSlug, datasetSlug, versionId } =
    props;
  const { data } = useWorkspaceDatasetFilesPageQuery({
    variables: { isSpecificVersion, workspaceSlug, datasetSlug, versionId },
  });
  if (!data || !data.datasetLink || !data.workspace) {
    return null;
  }
  const { datasetLink, workspace } = data;
  const { dataset } = datasetLink;
  const version = isSpecificVersion ? dataset.version! : dataset.latestVersion!;

  const currentFile = (() => {
    if (!fileId) {
      return version.files.items[0];
    } else {
      return version.files.items.find(
        (file: { id: string }) => file.id === fileId,
      );
    }
  })();

  return (
    <Page title={dataset.name ?? t("Dataset")}>
      <DatasetLayout
        datasetLink={datasetLink}
        workspace={workspace}
        version={version ?? null}
        extraBreadcrumbs={[
          {
            title: t("Files"),
            href: `/workspaces/${encodeURIComponent(
              workspace.slug,
            )}/datasets/${encodeURIComponent(datasetLink.dataset.slug)}/files`,
          },
        ]}
        tab="files"
      >
        <DatasetExplorer
          version={version}
          currentFile={currentFile}
          onClickFile={(file) =>
            router.push({
              pathname: `${router.pathname}`,
              query: { ...router.query, version: version?.id, fileId: file.id },
            })
          }
        />
      </DatasetLayout>
      <LinkDatasetDialog
        dataset={datasetLink.dataset}
        open={isLinkDialogOpen}
        onClose={() => setLinkDialogOpen(false)}
      />
    </Page>
  );
};

WorkspaceDatasetFilesPage.getLayout = (page) => page;

export const getServerSideProps = createGetServerSideProps({
  requireAuth: true,
  async getServerSideProps(ctx, client) {
    const versionId = (ctx.query.version as string) ?? "";

    const variables = {
      workspaceSlug: ctx.params!.workspaceSlug as string,
      datasetSlug: ctx.params!.datasetSlug as string,
      versionId: versionId,
      isSpecificVersion: Boolean(versionId),
    };

    const { data } = await client.query<
      WorkspaceDatasetFilesPageQuery,
      WorkspaceDatasetFilesPageQueryVariables
    >({
      query: WorkspaceDatasetFilesPageDocument,
      variables,
    });

    const version = variables.isSpecificVersion
      ? data.datasetLink?.dataset.version
      : data.datasetLink?.dataset.latestVersion;
    if (!data.datasetLink || !data.workspace || !version) {
      return { notFound: true };
    }

    // optional route parameters
    const fileArr = (ctx.query.fileId as string[]) ?? [];

    return {
      props: {
        ...variables,
        fileId: fileArr.length === 1 ? fileArr[0] : null,
      },
    };
  },
});

export default WorkspaceDatasetFilesPage;

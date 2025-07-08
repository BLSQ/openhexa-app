import Page from "core/components/Page";
import { createGetServerSideProps } from "core/helpers/page";
import { NextPageWithLayout } from "core/helpers/types";
import DatasetExplorer from "datasets/features/DatasetExplorer";
import { DatasetExplorer_FileFragment } from "datasets/features/DatasetExplorer/DatasetExplorer.generated";
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
  currentFile: NonNullable<DatasetExplorer_FileFragment>;
};

const DEFAULT_PAGE = 1;
const DEFAULT_PAGE_SIZE = 20;

const WorkspaceDatasetFilesPage: NextPageWithLayout = (
  props: WorkspaceDatasetFilesPageProps,
) => {
  const { t } = useTranslation();
  const router = useRouter();
  const [isLinkDialogOpen, setLinkDialogOpen] = useState(false);
  const page = parseInt(router.query.page as string) || DEFAULT_PAGE;
  const {
    currentFile,
    isSpecificVersion,
    workspaceSlug,
    datasetSlug,
    versionId,
  } = props;

  const { data } = useWorkspaceDatasetFilesPageQuery({
    variables: {
      isSpecificVersion,
      workspaceSlug,
      datasetSlug,
      versionId,
      page,
      perPage: DEFAULT_PAGE_SIZE,
    },
  });
  if (!data || !data.datasetLink || !data.workspace) {
    return null;
  }
  const { datasetLink, workspace } = data;
  const { dataset } = datasetLink;
  const version = isSpecificVersion ? dataset.version! : dataset.latestVersion!;

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
              query: {
                ...router.query,
                version: version?.id,
                fileId: file.id,
              },
            })
          }
          perPage={DEFAULT_PAGE_SIZE}
          onPageChange={(newPage) =>
            router.push({
              pathname: router.pathname,
              query: {
                ...router.query,
                page: newPage,
              },
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
    await DatasetLayout.prefetch(ctx, client);
    const versionId = (ctx.query.version as string) ?? "";

    const variables = {
      workspaceSlug: ctx.params!.workspaceSlug as string,
      datasetSlug: ctx.params!.datasetSlug as string,
      versionId: versionId,
      isSpecificVersion: Boolean(versionId),
      page: Number(ctx.query.page) || DEFAULT_PAGE,
      perPage: Number(ctx.query.perPage) || DEFAULT_PAGE_SIZE,
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
    try {
      const currentFileId = (ctx.query.fileId as string[])[0];
      const currentFile = version.files.items.find(
        (f) => f.id === currentFileId,
      );
      // If file not found on current page, redirect to first file of current page
      if (!currentFile && version.files.items.length > 0) {
        return {
          redirect: {
            destination: `/workspaces/${encodeURIComponent(
              data.workspace.slug,
            )}/datasets/${encodeURIComponent(data.datasetLink.dataset.slug)}/files/${encodeURIComponent(version.files.items[0].id)}?version=${encodeURIComponent(version.id)}&page=${variables.page}`,
            permanent: false,
          },
        };
      }
      if (!currentFile) {
        return { notFound: true };
      }
      return {
        props: {
          ...variables,
          currentFile,
        },
      };
    } catch (e) {
      if (version.files.items.length > 0) {
        return {
          redirect: {
            destination: `/workspaces/${encodeURIComponent(
              data.workspace.slug,
            )}/datasets/${encodeURIComponent(data.datasetLink.dataset.slug)}/files/${encodeURIComponent(version.files.items[0].id)}?version=${encodeURIComponent(version.id)}&page=${variables.page}`,
            permanent: false,
          },
        };
      }
      return {
        notFound: true,
      };
    }
  },
});

export default WorkspaceDatasetFilesPage;

import {
  ArrowDownTrayIcon,
  ArrowUpTrayIcon,
  DocumentIcon,
  FolderIcon,
  MagnifyingGlassIcon,
  TrashIcon,
} from "@heroicons/react/24/outline";
import Block from "core/components/Block";
import Breadcrumbs from "core/components/Breadcrumbs";
import Button from "core/components/Button";
import DataGrid, { BaseColumn } from "core/components/DataGrid";
import DateColumn from "core/components/DataGrid/DateColumn";
import { TextColumn } from "core/components/DataGrid/TextColumn";
import Link from "core/components/Link";
import MarkdownViewer from "core/components/MarkdownViewer";
import Page from "core/components/Page";
import { createGetServerSideProps } from "core/helpers/page";
import { NextPageWithLayout } from "core/helpers/types";
import { useTranslation } from "next-i18next";
import { useRouter } from "next/router";
import { useMemo } from "react";
import {
  getWorkspaceFile,
  WORKSPACES,
  SAMPLE_README_CONTENT,
} from "workspaces/helpers/fixtures";
import WorkspaceLayout from "workspaces/layouts/WorkspaceLayout";

type Props = {
  page: number;
  perPage: number;
};

const WorkspaceFilesPage: NextPageWithLayout = (props: Props) => {
  const { t } = useTranslation();
  const router = useRouter();
  const workspace = WORKSPACES.find((w) => w.id === router.query.workspaceId);

  const item = useMemo(() => {
    return workspace && router.query.id
      ? getWorkspaceFile(workspace.id, router.query.id)
      : null;
  }, [workspace, router.query.id]);

  if (!workspace) {
    return null;
  }

  const files = item?.children ?? workspace.files;
  return (
    <Page title={t("Workspace")}>
      <WorkspaceLayout.Header className="flex items-center justify-between">
        <Breadcrumbs withHome={false}>
          <Breadcrumbs.Part
            isFirst
            href={`/workspaces/${encodeURIComponent(workspace.id)}`}
          >
            {workspace.name}
          </Breadcrumbs.Part>
          <Breadcrumbs.Part
            href={`/workspaces/${encodeURIComponent(workspace.id)}/files`}
            isLast={item ? false : true}
          >
            {t("Files")}
          </Breadcrumbs.Part>
          {item && (
            <Breadcrumbs.Part
              href={`/workspaces/${encodeURIComponent(workspace.id)}/files`}
              isLast
            >
              {item.name}
            </Breadcrumbs.Part>
          )}
        </Breadcrumbs>
        <div className="flex items-center gap-2">
          <Button
            leadingIcon={<MagnifyingGlassIcon className="h-4 w-4" />}
            variant="white"
          >
            {t("Search")}
          </Button>
          <Button leadingIcon={<ArrowUpTrayIcon className="h-4 w-4" />}>
            {t("Upload")}
          </Button>
        </div>
      </WorkspaceLayout.Header>
      <WorkspaceLayout.PageContent className="space-y-4">
        {(!item || item.type === "folder") && (
          <Block className="divide divide-y divide-gray-100">
            <DataGrid
              data={files}
              defaultPageSize={10}
              totalItems={files.length}
              fixedLayout={false}
            >
              <BaseColumn id="name" label={t("Name")}>
                {(value) =>
                  value.type === "folder" ? (
                    <Link
                      noStyle
                      href={{
                        pathname: "/workspaces/[workspaceId]/files",
                        query: {
                          workspaceId: workspace.id,
                          id: value.id,
                        },
                      }}
                      className="flex items-center gap-1.5 font-medium text-gray-700 hover:text-gray-800"
                    >
                      <FolderIcon className="h-5 w-5" />
                      {value.name}
                    </Link>
                  ) : (
                    <div className="flex items-center gap-1.5 font-medium  text-gray-700">
                      <DocumentIcon className="h-5 w-5" />
                      {value.name}
                    </div>
                  )
                }
              </BaseColumn>
              <TextColumn
                accessor="type"
                label={t("Type")}
                id="type"
                className="capitalize"
              />
              <DateColumn
                accessor={"updatedAt"}
                label={t("Last updated")}
                relative
              />
              <BaseColumn id="actions">
                {() => (
                  <div className="flex flex-1 justify-end gap-2">
                    <Button
                      variant="outlined"
                      size="sm"
                      title={t("Delete")}
                      className="hover:bg-red-600 hover:text-white"
                    >
                      <TrashIcon className="h-4 w-4" />
                    </Button>
                    <Button variant="secondary" size="sm" title={t("Download")}>
                      <ArrowDownTrayIcon className="h-4 w-4" />
                    </Button>
                  </div>
                )}
              </BaseColumn>
            </DataGrid>
          </Block>
        )}
        {!item && (
          <Block className="divide divide-y divide-gray-100">
            <Block.Header>README.md</Block.Header>
            <Block.Content>
              <MarkdownViewer className="prose-sm">
                {SAMPLE_README_CONTENT}
              </MarkdownViewer>
            </Block.Content>
          </Block>
        )}
      </WorkspaceLayout.PageContent>
    </Page>
  );
};

WorkspaceFilesPage.getLayout = (page, pageProps) => {
  return <WorkspaceLayout pageProps={pageProps}>{page}</WorkspaceLayout>;
};

export const getServerSideProps = createGetServerSideProps({
  requireAuth: true,
});

export default WorkspaceFilesPage;

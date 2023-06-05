import { EyeIcon } from "@heroicons/react/24/outline";
import Block from "core/components/Block";
import Breadcrumbs from "core/components/Breadcrumbs";
import Button from "core/components/Button";
import DataGrid from "core/components/DataGrid";
import { TextColumn } from "core/components/DataGrid/TextColumn";
import Page from "core/components/Page";
import { createGetServerSideProps } from "core/helpers/page";
import { NextPageWithLayout } from "core/helpers/types";
import { useTranslation } from "next-i18next";
import { useRouter } from "next/router";
import { useState } from "react";
import DataPreviewDialog from "workspaces/features/DataPreviewDialog";
import {
  useWorkspaceDatabaseTablePageQuery,
  WorkspaceDatabaseTablePageDocument,
} from "workspaces/graphql/queries.generated";
import WorkspaceLayout from "workspaces/layouts/WorkspaceLayout";

type Props = {
  page: number;
  perPage: number;
};

const WorkspaceDatabaseTableViewPage: NextPageWithLayout = (props: Props) => {
  const { t } = useTranslation();
  const [openModal, setOpenModal] = useState(false);
  const router = useRouter();
  const { data } = useWorkspaceDatabaseTablePageQuery({
    variables: {
      workspaceSlug: router.query.workspaceSlug as string,
      tableName: router.query.tableId as string,
    },
  });

  if (!data?.workspace) {
    return null;
  }
  const { workspace } = data;
  const { table } = workspace.database;
  if (!table) {
    return null;
  }

  const handleOpenModal = () => {
    setOpenModal(!openModal);
  };

  return (
    <Page title={table.name}>
      <WorkspaceLayout workspace={workspace}>
        <WorkspaceLayout.Header className="flex items-center justify-between">
          <Breadcrumbs withHome={false}>
            <Breadcrumbs.Part
              isFirst
              href={`/workspaces/${encodeURIComponent(workspace.slug)}`}
            >
              {workspace.name}
            </Breadcrumbs.Part>
            <Breadcrumbs.Part
              href={`/workspaces/${encodeURIComponent(
                workspace.slug
              )}/databases`}
            >
              {t("Database")}
            </Breadcrumbs.Part>
            <Breadcrumbs.Part
              isLast
              href={`/workspaces/${encodeURIComponent(
                workspace.slug
              )}/databases/${router.query.tableId}`}
            >
              {table.name}
            </Breadcrumbs.Part>
          </Breadcrumbs>
          <div className="flex items-center gap-2">
            <Button
              onClick={handleOpenModal}
              leadingIcon={<EyeIcon className="w-4" />}
            >
              {t("Preview data")}
            </Button>
          </div>
        </WorkspaceLayout.Header>
        <WorkspaceLayout.PageContent className="space-y-4">
          <Block className="divide-y-2 divide-gray-100">
            <Block.Content title={t("Definition")}>
              <DataGrid
                data={table.columns}
                fixedLayout={false}
                totalItems={table.columns.length}
                className="w-3/4 max-w-lg rounded-md border"
              >
                <TextColumn
                  className="py-3 font-mono"
                  textClassName="bg-gray-50 py-1 px-2"
                  name="field"
                  label="Field"
                  accessor="name"
                />
                <TextColumn
                  className="py-3"
                  name="type"
                  label="Type"
                  accessor="type"
                />
              </DataGrid>
            </Block.Content>
          </Block>
          <DataPreviewDialog
            open={openModal}
            onClose={() => setOpenModal(!openModal)}
            workspaceSlug={workspace.slug}
            tableName={table.name}
          />
        </WorkspaceLayout.PageContent>
      </WorkspaceLayout>
    </Page>
  );
};

WorkspaceDatabaseTableViewPage.getLayout = (page) => page;

export const getServerSideProps = createGetServerSideProps({
  requireAuth: true,
  async getServerSideProps(ctx, client) {
    await WorkspaceLayout.prefetch(ctx, client);
    const { data } = await client.query({
      query: WorkspaceDatabaseTablePageDocument,
      variables: {
        workspaceSlug: ctx.params?.workspaceSlug,
        tableName: ctx.params?.tableId,
      },
    });

    if (!data.workspace?.database.table) {
      return {
        notFound: true,
      };
    }
  },
});

export default WorkspaceDatabaseTableViewPage;

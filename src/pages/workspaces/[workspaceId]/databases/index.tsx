import { TableCellsIcon } from "@heroicons/react/24/outline";
import Breadcrumbs from "core/components/Breadcrumbs";
import DataGrid, { BaseColumn } from "core/components/DataGrid";
import ChevronLinkColumn from "core/components/DataGrid/ChevronLinkColumn";
import DateColumn from "core/components/DataGrid/DateColumn";
import { TextColumn } from "core/components/DataGrid/TextColumn";
import Page from "core/components/Page";
import Title from "core/components/Title";
import { createGetServerSideProps } from "core/helpers/page";
import { NextPageWithLayout } from "core/helpers/types";
import { useTranslation } from "next-i18next";
import { useRouter } from "next/router";
import { WORKSPACES } from "workspaces/helpers/fixtures";
import WorkspaceLayout from "workspaces/layouts/WorkspaceLayout";

type Props = {
  page: number;
  perPage: number;
};

const WorkspaceDatabasesPage: NextPageWithLayout = (props: Props) => {
  const { t } = useTranslation();
  const router = useRouter();
  const workspace = WORKSPACES.find((w) => w.id === router.query.workspaceId);

  if (!workspace) {
    return null;
  }

  return (
    <Page title={t("Workspace")}>
      <WorkspaceLayout.Header>
        <Breadcrumbs withHome={false}>
          <Breadcrumbs.Part
            isFirst
            href={`/workspaces/${encodeURIComponent(workspace.id)}`}
          >
            {workspace.name}
          </Breadcrumbs.Part>
          <Breadcrumbs.Part
            href={`/workspaces/${encodeURIComponent(workspace.id)}/databases`}
          >
            {t("Database")}
          </Breadcrumbs.Part>
        </Breadcrumbs>
      </WorkspaceLayout.Header>
      <WorkspaceLayout.PageContent className="space-y-8">
        <div className="flex flex-1 items-center justify-between">
          <Title level={2}>{t("Database")}</Title>
        </div>
        <div>
          <Title level={5}> {t("Workspace tables")}</Title>
          <DataGrid
            className="bg-white shadow"
            data={workspace.database.workspaceTables}
            defaultPageSize={5}
            sortable
            totalItems={workspace.database.workspaceTables.length}
            fixedLayout={false}
          >
            <TextColumn
              className="max-w-[50ch] py-3"
              textClassName="font-medium text-gray-600"
              accessor={(value) => (
                <>
                  <div className="flex space-x-2">
                    <TableCellsIcon className="h-6 w-6" />
                    <span className="font-medium text-gray-800">
                      {value.name}
                    </span>
                  </div>
                </>
              )}
              id="name"
              label="Name"
            />

            <BaseColumn
              className="py-3"
              accessor="content"
              id="content"
              label="Content"
            >
              {(value) => <span>{`${value} row(s)`}</span>}
            </BaseColumn>

            <DateColumn
              className="py-3"
              accessor="updatedAt"
              relative
              id="updatedAt"
              label="Last modified"
            />
            <ChevronLinkColumn
              maxWidth="100"
              accessor="id"
              url={(value: any) => ({
                pathname: `${router.asPath}/[tableId]`,
                query: { tableId: value },
              })}
            />
          </DataGrid>
        </div>

        <div>
          <Title level={5}>{t("Shared tables")}</Title>
          <DataGrid
            className="bg-white shadow-md"
            data={workspace.database.sharedTables}
            defaultPageSize={5}
            sortable
            totalItems={workspace.database.sharedTables.length}
            fixedLayout={false}
          >
            <TextColumn
              className="max-w-[50ch] py-3 "
              textClassName="font-medium text-gray-600"
              accessor={(value) => (
                <>
                  <div className="flex space-x-2">
                    <TableCellsIcon className="h-6 w-6" />
                    <span className="font-medium text-gray-800">
                      {value.name}
                    </span>
                  </div>
                </>
              )}
              id="name"
              label="Name"
            />
            <BaseColumn
              className="py-3"
              accessor="content"
              id="content"
              label="Content"
            >
              {(value) => <div>{`${value} row(s)`}</div>}
            </BaseColumn>
            <DateColumn
              className="py-3"
              relative
              accessor="updatedAt"
              id="updatedAt"
              label="Last modified"
            />
            <ChevronLinkColumn
              maxWidth="100"
              accessor="id"
              url={(value: any) => ({
                pathname: "/databases/[tableId]",
                query: { tableId: value },
              })}
            />
          </DataGrid>
        </div>
      </WorkspaceLayout.PageContent>
    </Page>
  );
};

WorkspaceDatabasesPage.getLayout = (page, pageProps) => {
  return <WorkspaceLayout pageProps={pageProps}>{page}</WorkspaceLayout>;
};

export const getServerSideProps = createGetServerSideProps({
  requireAuth: true,
});

export default WorkspaceDatabasesPage;

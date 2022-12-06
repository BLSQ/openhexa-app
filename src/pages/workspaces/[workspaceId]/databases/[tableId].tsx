import Block from "core/components/Block";
import Breadcrumbs from "core/components/Breadcrumbs";
import CodeEditor from "core/components/CodeEditor";
import DataGrid from "core/components/DataGrid";
import { TextColumn } from "core/components/DataGrid/TextColumn";
import Page from "core/components/Page";
import Tabs from "core/components/Tabs";
import Title from "core/components/Title";
import { createGetServerSideProps } from "core/helpers/page";
import { NextPageWithLayout } from "core/helpers/types";
import { capitalize } from "lodash";
import { useTranslation } from "next-i18next";
import { useRouter } from "next/router";
import { WORKSPACES } from "workspaces/helpers/fixtures";
import WorkspaceLayout from "workspaces/layouts/WorkspaceLayout";

type Props = {
  page: number;
  perPage: number;
};

const WorkspaceDatabaseTableViewPage: NextPageWithLayout = (props: Props) => {
  const { t } = useTranslation();
  const router = useRouter();
  const workspace = WORKSPACES.find((w) => w.id === router.query.workspaceId);

  if (!workspace) {
    return null;
  }

  const table = [
    ...workspace.database.sharedTables,
    ...workspace.database.workspaceTables,
  ].find((t) => t.id === router.query.tableId);
  if (!table) {
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
          <Breadcrumbs.Part
            href={`/workspaces/${encodeURIComponent(workspace.id)}/databases/${
              router.query.tableId
            }`}
          >
            {capitalize(table.name)}
          </Breadcrumbs.Part>
        </Breadcrumbs>
      </WorkspaceLayout.Header>
      <WorkspaceLayout.PageContent className="space-y-8">
        <div>
          <Title level={2}>{capitalize(table.name)}</Title>
        </div>
        <Block className="p-4">
          <div className="text-gray-600">
            <p>{t("Database table")}</p>
          </div>
          <Tabs defaultIndex={0}>
            <Tabs.Tab className="mt-4" label={t("Information")}>
              <div className="mt-5 text-sm text-gray-600">
                <p>{table.description}</p>
              </div>
              <DataGrid
                data={table.schema}
                fixedLayout={false}
                className="mt-4 w-1/4 border-2 border-solid"
              >
                <TextColumn
                  className="py-3 font-medium"
                  name="field"
                  label="Field"
                  accessor="fieldName"
                />
                <TextColumn
                  className="py-3"
                  name="type"
                  label="Type"
                  accessor="type"
                />
              </DataGrid>
            </Tabs.Tab>
            <Tabs.Tab className="mt-4" label={t("Code samples")}>
              <div className="mt-5">
                <CodeEditor readonly lang="json" value={table.codeSample[0]} />
              </div>
            </Tabs.Tab>
            <Tabs.Tab className="mt-4" label={t("Use in BI tools")}>
              <div className="mt-5">
                <CodeEditor readonly lang="json" value={table.codeSample[1]} />
              </div>
            </Tabs.Tab>
          </Tabs>
        </Block>
        <Block className="p-4">
          <div className="text-gray-600">
            <p>{t("Data preview")}</p>
          </div>
          <DataGrid data={table.schema} fixedLayout={false} className="mt-4">
            {table.schema.map((s, index) => (
              <TextColumn
                key={index}
                className="py-3 font-medium"
                name={s.fieldName}
                label={s.fieldName}
                accessor="sample"
              />
            ))}
          </DataGrid>
        </Block>
      </WorkspaceLayout.PageContent>
    </Page>
  );
};

WorkspaceDatabaseTableViewPage.getLayout = (page, pageProps) => {
  return <WorkspaceLayout pageProps={pageProps}>{page}</WorkspaceLayout>;
};

export const getServerSideProps = createGetServerSideProps({
  requireAuth: true,
});

export default WorkspaceDatabaseTableViewPage;

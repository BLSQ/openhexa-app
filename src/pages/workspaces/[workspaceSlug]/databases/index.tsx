import { TableCellsIcon } from "@heroicons/react/24/outline";
import Block from "core/components/Block";
import Breadcrumbs from "core/components/Breadcrumbs";
import CodeEditor from "core/components/CodeEditor";
import DataGrid, { BaseColumn } from "core/components/DataGrid";
import ChevronLinkColumn from "core/components/DataGrid/ChevronLinkColumn";
import Link from "core/components/Link";
import Page from "core/components/Page";
import Tabs from "core/components/Tabs";
import Title from "core/components/Title";
import { createGetServerSideProps } from "core/helpers/page";
import { NextPageWithLayout } from "core/helpers/types";
import { useTranslation } from "next-i18next";
import { useRouter } from "next/router";
import {
  useWorkspaceDatabasesPageQuery,
  WorkspaceDatabasesPageDocument,
} from "workspaces/graphql/queries.generated";
import {
  getReadTableSnippet,
  getUsageSnippet,
} from "workspaces/helpers/database";
import WorkspaceLayout from "workspaces/layouts/WorkspaceLayout";

type Props = {
  workspaceSlug: string;
  page?: number;
};

const WorkspaceDatabasesPage: NextPageWithLayout = (props: Props) => {
  const router = useRouter();

  const { t } = useTranslation();
  const { data, refetch } = useWorkspaceDatabasesPageQuery({
    variables: { workspaceSlug: props.workspaceSlug, page: props.page },
  });

  const onChangePage = ({ page }: { page: number }) => {
    refetch({
      workspaceSlug: props.workspaceSlug,
      page,
    });
  };

  if (!data?.workspace) {
    return null;
  }
  const { workspace } = data;
  const { tables } = workspace.database;

  return (
    <Page title={t("Workspace")}>
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
              isLast
              href={`/workspaces/${encodeURIComponent(
                workspace.slug
              )}/databases`}
            >
              {t("Database")}
            </Breadcrumbs.Part>
          </Breadcrumbs>
        </WorkspaceLayout.Header>
        <WorkspaceLayout.PageContent className="space-y-8">
          <Title level={2}>{t("Tables")}</Title>
          <DataGrid
            className="overflow-hidden rounded-md bg-white shadow"
            data={tables.items}
            defaultPageSize={15}
            sortable
            totalItems={tables.totalItems}
            fixedLayout={false}
            fetchData={onChangePage}
          >
            <BaseColumn
              className="max-w-[50ch] py-3"
              textClassName="font-medium text-gray-600"
              id="name"
              label="Name"
            >
              {(value) => (
                <Link
                  href={{
                    pathname: "/workspaces/[workspaceSlug]/databases/[tableId]",
                    query: {
                      workspaceSlug: workspace.slug,
                      tableId: value.name,
                    },
                  }}
                >
                  <div className="flex items-center gap-3">
                    <TableCellsIcon className="h-6 w-6 text-gray-500" />
                    <span className="font-medium text-gray-700">
                      {value.name}
                    </span>
                  </div>
                </Link>
              )}
            </BaseColumn>
            <BaseColumn
              className="py-3"
              accessor="count"
              id="content"
              label={t("# Rows")}
            >
              {(value) => (
                <span>
                  {t("Approx. {{count}} row", {
                    count: value,
                    plural: "Approx. {{count}} rows",
                  })}
                </span>
              )}
            </BaseColumn>
            <ChevronLinkColumn
              maxWidth="100"
              accessor="name"
              url={(value: any) => ({
                pathname: `/workspaces/${encodeURIComponent(
                  workspace.slug
                )}/databases/[tableId]`,
                query: { tableId: value },
              })}
            />
          </DataGrid>
          <Block>
            <Block.Section collapsible={false} title={t("Usage")}>
              <Tabs defaultIndex={0}>
                <Tabs.Tab label={t("Create table")}>
                  <CodeEditor
                    readonly
                    lang="python"
                    value={getUsageSnippet("table", "PYTHON")}
                  />
                </Tabs.Tab>
                <Tabs.Tab label={t("Read table")}>
                  <CodeEditor
                    readonly
                    lang="python"
                    value={getReadTableSnippet("table")}
                  />
                </Tabs.Tab>
                <Tabs.Tab label={t("Use in BI tools")}>
                  <CodeEditor
                    readonly
                    lang="r"
                    value={getUsageSnippet("table", "R")}
                  />
                </Tabs.Tab>
              </Tabs>
            </Block.Section>
          </Block>
        </WorkspaceLayout.PageContent>
      </WorkspaceLayout>
    </Page>
  );
};

WorkspaceDatabasesPage.getLayout = (page) => page;

export const getServerSideProps = createGetServerSideProps({
  requireAuth: true,
  async getServerSideProps(ctx, client) {
    await WorkspaceLayout.prefetch(client);
    const { data } = await client.query({
      query: WorkspaceDatabasesPageDocument,
      variables: {
        workspaceSlug: ctx.params?.workspaceSlug,
        page: ctx.query.page ?? 1,
      },
    });

    if (!data.workspace) {
      return {
        notFound: true,
      };
    }
    return {
      props: { workspaceSlug: data.workspace.slug, page: ctx.query.page ?? 1 },
    };
  },
});

export default WorkspaceDatabasesPage;

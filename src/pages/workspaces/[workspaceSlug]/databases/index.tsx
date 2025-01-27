import { TableCellsIcon } from "@heroicons/react/24/outline";
import Block from "core/components/Block";
import Breadcrumbs from "core/components/Breadcrumbs";
import DataGrid, { BaseColumn } from "core/components/DataGrid";
import ChevronLinkColumn from "core/components/DataGrid/ChevronLinkColumn";
import Link from "core/components/Link";
import Page from "core/components/Page";
import Title from "core/components/Title";
import { createGetServerSideProps } from "core/helpers/page";
import { NextPageWithLayout } from "core/helpers/types";
import { useTranslation } from "next-i18next";
import DatabaseVariablesSection from "workspaces/features/DatabaseVariablesSection";
import {
  useWorkspaceDatabasesPageQuery,
  WorkspaceDatabasesPageDocument,
} from "workspaces/graphql/queries.generated";
import WorkspaceLayout from "workspaces/layouts/WorkspaceLayout";

type Props = {
  workspaceSlug: string;
  page?: number;
};

const WorkspaceDatabasesPage: NextPageWithLayout = (props: Props) => {
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
    <Page title={workspace.name}>
      <WorkspaceLayout
        workspace={workspace}
        helpLinks={[
          {
            label: t("About the workspace database"),
            href: "https://github.com/BLSQ/openhexa/wiki/User-manual#using-the-workspaces-database",
          },
          {
            label: t("Using the workspace database in pipelines"),
            href: "https://github.com/BLSQ/openhexa/wiki/Writing-OpenHEXA-pipelines#using-the-workspace-database",
          },
          {
            label: t("Using the workspace database in notebooks"),
            href: "https://github.com/BLSQ/openhexa/wiki/Using-notebooks-in-OpenHEXA#using-the-workspace-database",
          },
        ]}
        header={
          <>
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
                  workspace.slug,
                )}/databases`}
              >
                {t("Database")}
              </Breadcrumbs.Part>
            </Breadcrumbs>
          </>
        }
      >
        <WorkspaceLayout.PageContent className="space-y-8">
          <Title level={2}>{t("Tables")}</Title>
          <DataGrid
            className="overflow-hidden rounded-md bg-white shadow-xs"
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
              label={t("Name")}
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
                  {t("{{count}} row", {
                    count: value,
                    plural: "{{count}} rows",
                  })}
                </span>
              )}
            </BaseColumn>
            <ChevronLinkColumn
              maxWidth="100"
              accessor="name"
              url={(value: any) => ({
                pathname: `/workspaces/${encodeURIComponent(
                  workspace.slug,
                )}/databases/[tableId]`,
                query: { tableId: value },
              })}
            />
          </DataGrid>
          <Block className="divide-y-2">
            {workspace.permissions.update && (
              <Block.Section
                collapsible={false}
                title={t("Connection parameters")}
              >
                <DatabaseVariablesSection workspace={workspace} />
              </Block.Section>
            )}
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
    await WorkspaceLayout.prefetch(ctx, client);
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

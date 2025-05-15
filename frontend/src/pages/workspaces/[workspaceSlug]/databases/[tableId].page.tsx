import { TrashIcon, ViewColumnsIcon } from "@heroicons/react/24/outline";
import Block from "core/components/Block";
import Breadcrumbs from "core/components/Breadcrumbs";
import Button from "core/components/Button";
import Page from "core/components/Page";
import Popover from "core/components/Popover/Popover";
import Checkbox from "core/components/forms/Checkbox/Checkbox";
import { trackEvent } from "core/helpers/analytics";
import { createGetServerSideProps } from "core/helpers/page";
import { NextPageWithLayout } from "core/helpers/types";
import { OrderByDirection } from "graphql/types";
import { useTranslation } from "next-i18next";
import { useRouter } from "next/router";
import { useEffect, useMemo, useState } from "react";
import DatabaseTableDataGrid from "workspaces/features/DatabaseTableDataGrid/DatabaseTableDataGrid";
import DeleteDatabaseTableTrigger from "workspaces/features/DeleteDatabaseTableTrigger";
import {
  WorkspaceDatabaseTablePageDocument,
  WorkspaceDatabaseTablePageQuery,
  useWorkspaceDatabaseTablePageQuery,
} from "workspaces/graphql/queries.generated";
import WorkspaceLayout from "workspaces/layouts/WorkspaceLayout";

type Props = {
  page: number;
  direction: OrderByDirection;
  orderBy: string;
};

const WorkspaceDatabaseTableViewPage: NextPageWithLayout = ({
  page,
  direction,
  orderBy,
}: Props) => {
  const { t } = useTranslation();
  const router = useRouter();
  const { data } = useWorkspaceDatabaseTablePageQuery({
    variables: {
      workspaceSlug: router.query.workspaceSlug as string,
      tableName: router.query.tableId as string,
    },
  });

  const [displayColumns, setDisplayColumns] = useState<
    { name: string; type: string }[]
  >(data?.workspace?.database.table?.columns ?? []);

  const columns = useMemo(() => {
    const arr = [...(data?.workspace?.database.table?.columns ?? [])];
    arr.sort((a, b) => (a.name > b.name ? 1 : -1));
    return arr;
  }, [data]);

  useEffect(() => {
    if (data?.workspace) {
      trackEvent("databases.table_viewed", {
        workspace: data.workspace.slug,
        table_name: table?.name,
      });
    }
  }, []);

  if (!data?.workspace) {
    return null;
  }
  const { workspace } = data;
  const { table } = workspace.database;

  if (!table) {
    return null;
  }

  return (
    <Page title={table.name}>
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
                href={`/workspaces/${encodeURIComponent(
                  workspace.slug,
                )}/databases`}
              >
                {t("Database")}
              </Breadcrumbs.Part>
              <Breadcrumbs.Part
                isLast
                href={`/workspaces/${encodeURIComponent(
                  workspace.slug,
                )}/databases/${router.query.tableId}`}
              >
                {table.name}
              </Breadcrumbs.Part>
            </Breadcrumbs>
            <DeleteDatabaseTableTrigger workspace={workspace} table={table}>
              {({ onClick }) => (
                <Button
                  className="bg-red-500 hover:bg-red-700 focus:ring-red-500"
                  onClick={onClick}
                  leadingIcon={<TrashIcon className="w-4" />}
                >
                  {t("Delete")}
                </Button>
              )}
            </DeleteDatabaseTableTrigger>
          </>
        }
      >
        <WorkspaceLayout.PageContent className="space-y-4">
          <div className="flex justify-end">
            <Popover
              placement="bottom-start"
              withPortal
              as="div"
              trigger={
                <Button leadingIcon={<ViewColumnsIcon className="h-4 w-4" />}>
                  {t("Select columns")}
                </Button>
              }
            >
              <p className="mb-2 text-sm">
                {t("Select the columns to display in the grid")}
              </p>
              <div className="max-h-96 overflow-y-auto pb-2 ">
                {columns.map((column) => (
                  <div key={column.name} className="flex items-center py-1.5">
                    <Checkbox
                      name={column.name}
                      label={column.name}
                      checked={displayColumns.some(
                        (c) => c.name === column.name,
                      )}
                      onChange={(event) =>
                        event.target.checked
                          ? setDisplayColumns([...displayColumns, column])
                          : setDisplayColumns(
                              displayColumns.filter(
                                (c) => c.name !== column.name,
                              ),
                            )
                      }
                    />
                  </div>
                ))}
              </div>
              <div className="mt-2 flex justify-end gap-2 ">
                <Button
                  size="sm"
                  variant="outlined"
                  onClick={() => setDisplayColumns(columns)}
                >
                  {t("Select all")}
                </Button>
                <Button
                  size="sm"
                  variant="outlined"
                  onClick={() => setDisplayColumns([])}
                >
                  {t("Select none")}
                </Button>
              </div>
            </Popover>
          </div>
          <Block className="px-6 py-5">
            {table.columns.length > 0 ? (
              <DatabaseTableDataGrid
                workspace={workspace}
                columns={displayColumns}
                table={table}
                page={page}
                className="-mx-6 -mt-5"
                direction={direction}
                orderBy={orderBy}
                onChange={(options) =>
                  router.push({
                    pathname: router.pathname,
                    query: {
                      ...router.query,
                      ...options,
                    },
                  })
                }
              />
            ) : (
              <p>{t("This table has no columns")}</p>
            )}
          </Block>
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
    const { data } = await client.query<WorkspaceDatabaseTablePageQuery>({
      query: WorkspaceDatabaseTablePageDocument,
      variables: {
        workspaceSlug: ctx.params?.workspaceSlug,
        tableName: ctx.params?.tableId,
      },
    });

    const { workspace } = data ?? {};
    if (!workspace?.database.table) {
      return {
        notFound: true,
      };
    }
    if (!ctx.query.orderBy && workspace.database.table.columns.length > 0) {
      return {
        redirect: {
          permanent: false,
          destination:
            ctx.resolvedUrl +
            "?orderBy=" +
            encodeURIComponent(workspace.database.table.columns[0].name),
        },
      };
    } else if (workspace.database.table.columns.length > 0) {
      const variables = {
        workspaceSlug: workspace.slug,
        tableName: ctx.params?.tableId as string,
        orderBy: ctx.query.orderBy as string,
        direction:
          (ctx.query.direction as OrderByDirection) || OrderByDirection.Asc,
        page: ctx.query.page ? parseInt(ctx.query.page as string, 10) : 1,
      };

      await DatabaseTableDataGrid.prefetch(client, variables);
      return {
        props: variables,
      };
    }
  },
});

export default WorkspaceDatabaseTableViewPage;

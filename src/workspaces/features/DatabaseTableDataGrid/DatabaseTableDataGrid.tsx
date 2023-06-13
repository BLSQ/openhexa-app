import { gql, useQuery } from "@apollo/client";
import clsx from "clsx";
import DataGrid from "core/components/DataGrid/DataGrid";
import { TextColumn } from "core/components/DataGrid/TextColumn";
import { SimplePagination } from "core/components/Pagination";
import { OrderByDirection } from "graphql-types";
import { useRouter } from "next/router";
import {
  DatabaseTableDataGridQuery,
  DatabaseTableDataGrid_TableFragment,
  DatabaseTableDataGrid_WorkspaceFragment,
} from "./DatabaseTableDataGrid.generated";

type DatabaseTableDataGridProps = {
  table: DatabaseTableDataGrid_TableFragment;
  workspace: DatabaseTableDataGrid_WorkspaceFragment;
  className?: string;
};

const DatabaseTableDataGrid = (props: DatabaseTableDataGridProps) => {
  const { table, workspace, className } = props;
  const router = useRouter();

  const variables = {
    slug: workspace.slug,
    tableName: table.name,
    orderBy: (router.query.column as string) ?? table.columns[0].name,
    direction: router.query.dir ?? OrderByDirection.Asc,
    page: router.query.page ? parseInt(router.query.page as string, 10) : 1,
    perPage: 15,
  };

  const { data } = useQuery<DatabaseTableDataGridQuery>(
    gql`
      query DatabaseTableDataGrid(
        $slug: String!
        $tableName: String!
        $orderBy: String!
        $direction: OrderByDirection!
        $page: Int!
        $perPage: Int
      ) {
        workspace(slug: $slug) {
          slug
          database {
            table(name: $tableName) {
              rows(
                orderBy: $orderBy
                direction: $direction
                page: $page
                perPage: $perPage
              ) {
                pageNumber
                hasNextPage
                hasPreviousPage
                items
              }
            }
          }
        }
      }
    `,
    {
      variables,
    }
  );

  const onSort = ({ sortBy }: any) => {
    router.push({
      pathname: `/workspaces/[workspaceSlug]/databases/[tableId]`,
      query: {
        ...router.query,
        page: 1,
        column: sortBy[0].id,
        dir: sortBy[0].desc ? OrderByDirection.Desc : OrderByDirection.Asc,
      },
    });
  };

  const { rows } = data?.workspace?.database?.table ?? {};
  if (!rows) {
    return null;
  }

  return (
    <div>
      <DataGrid
        data={rows.items ?? []}
        defaultPageSize={20}
        defaultSortBy={[
          {
            id: variables.orderBy,
            desc: variables.direction === OrderByDirection.Desc,
          },
        ]}
        className={clsx(className)}
        sortable
        fetchData={onSort}
      >
        {table.columns.map((column) => (
          <TextColumn
            id={column.name}
            key={column.name}
            name={column.name}
            label={column.name}
            accessor={column.name}
          />
        ))}
      </DataGrid>
      <SimplePagination
        hasNextPage={rows.hasNextPage ?? false}
        hasPreviousPage={rows.hasPreviousPage ?? false}
        page={variables.page}
        onChange={(page) => {
          router.push({
            pathname: `/workspaces/[workspaceSlug]/databases/[tableId]`,
            query: {
              ...router.query,
              page,
            },
          });
        }}
      />
    </div>
  );
};

DatabaseTableDataGrid.fragments = {
  workspace: gql`
    fragment DatabaseTableDataGrid_workspace on Workspace {
      slug
    }
  `,
  table: gql`
    fragment DatabaseTableDataGrid_table on DatabaseTable {
      name
      columns {
        name
        type
      }
    }
  `,
};

export default DatabaseTableDataGrid;

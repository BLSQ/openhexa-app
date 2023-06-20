import { gql } from "@apollo/client";
import clsx from "clsx";
import DataGrid from "core/components/DataGrid/DataGrid";
import { TextColumn } from "core/components/DataGrid/TextColumn";
import { SimplePagination } from "core/components/Pagination";
import { CustomApolloClient } from "core/helpers/apollo";
import { OrderByDirection } from "graphql-types";
import {
  DatabaseTableDataGrid_TableFragment,
  DatabaseTableDataGrid_WorkspaceFragment,
  useDatabaseTableDataGridQuery,
} from "./DatabaseTableDataGrid.generated";

type DatabaseTableDataGridProps = {
  table: DatabaseTableDataGrid_TableFragment;
  workspace: DatabaseTableDataGrid_WorkspaceFragment;
  className?: string;
  orderBy: string;
  direction: OrderByDirection;
  page: number;
  onChange(params: {
    page: number;
    orderBy?: string;
    direction?: OrderByDirection;
  }): void;
};

const DatabaseTableDataGrid = (props: DatabaseTableDataGridProps) => {
  const { table, workspace, className, orderBy, direction, page, onChange } =
    props;

  const { data } = useDatabaseTableDataGridQuery({
    variables: {
      workspaceSlug: workspace.slug,
      orderBy,
      direction,
      page,
      tableName: table.name,
    },
  });

  const onSort = ({ sortBy }: any) => {
    if (sortBy.length > 0) {
      onChange({
        page: 1,
        orderBy: sortBy[0].id,
        direction: sortBy[0].desc
          ? OrderByDirection.Desc
          : OrderByDirection.Asc,
      });
    } else {
      onChange({
        page: 1,
        orderBy: table.columns[0].name,
        direction: OrderByDirection.Desc,
      });
    }
  };

  const { rows } = data?.workspace?.database?.table ?? {};
  if (!rows) {
    return null;
  }

  return (
    <div>
      <DataGrid
        data={rows.items ?? []}
        defaultPageSize={10}
        defaultSortBy={[
          {
            id: orderBy,
            desc: direction === OrderByDirection.Desc,
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
        page={page}
        onChange={(page) => onChange({ page, orderBy, direction })}
      />
    </div>
  );
};

type PrefetchVariables = {
  workspaceSlug: string;
  tableName: string;
  orderBy: string;
  direction: OrderByDirection;
  page?: number;
};

DatabaseTableDataGrid.prefetch = async (
  client: CustomApolloClient,
  variables: PrefetchVariables
) => {
  await client.query({
    query: gql`
      query DatabaseTableDataGrid(
        $workspaceSlug: String!
        $tableName: String!
        $orderBy: String!
        $direction: OrderByDirection!
        $page: Int!
      ) {
        workspace(slug: $workspaceSlug) {
          slug
          database {
            table(name: $tableName) {
              rows(
                orderBy: $orderBy
                direction: $direction
                page: $page
                perPage: 10
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
    variables,
  });
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

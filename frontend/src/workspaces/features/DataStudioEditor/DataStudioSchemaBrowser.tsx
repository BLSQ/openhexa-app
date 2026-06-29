import { gql } from "@apollo/client";
import {
  ChevronDownIcon,
  ChevronRightIcon,
  CircleStackIcon,
  TableCellsIcon,
} from "@heroicons/react/24/outline";
import Spinner from "core/components/Spinner";
import clsx from "clsx";
import { useTranslation } from "next-i18next";
import { useMemo, useState } from "react";
import {
  useWorkspaceDataStudioSchemaQuery,
  useWorkspaceDataStudioTableColumnsQuery,
} from "./DataStudioSchemaBrowser.generated";

type DataStudioSchemaBrowserProps = {
  workspaceSlug: string;
  className?: string;
  onInsert(text: string): void;
};

type SchemaTableRowProps = {
  workspaceSlug: string;
  name: string;
  onInsert(text: string): void;
};

// Columns are fetched per table only once a row is expanded: introspecting every
// table up front is an expensive per-table round trip on the workspace database.
const SchemaTableRow = ({
  workspaceSlug,
  name,
  onInsert,
}: SchemaTableRowProps) => {
  const { t } = useTranslation();
  const [open, setOpen] = useState(false);

  const { data, loading } = useWorkspaceDataStudioTableColumnsQuery({
    variables: { workspaceSlug, table: name },
    skip: !open,
  });
  const columns = data?.workspace?.database?.table?.columns ?? [];

  return (
    <div>
      <div className="group flex items-center rounded hover:bg-gray-100">
        <button
          onClick={() => setOpen((value) => !value)}
          className="flex flex-1 items-center gap-1.5 px-2 py-1.5 text-left"
        >
          {open ? (
            <ChevronDownIcon className="h-3 w-3 text-gray-400" />
          ) : (
            <ChevronRightIcon className="h-3 w-3 text-gray-400" />
          )}
          <TableCellsIcon className="h-3.5 w-3.5 text-gray-400 group-hover:text-blue-600" />
          <span className="flex-1 truncate text-gray-700">{name}</span>
        </button>
        <button
          onClick={() => onInsert(name)}
          title={t("Insert into editor")}
          className="px-2 py-1.5 text-xs text-blue-600 opacity-0 hover:underline group-hover:opacity-100 focus-visible:opacity-100"
        >
          {t("Insert")}
        </button>
      </div>
      {open &&
        (loading ? (
          <div className="flex justify-center py-2">
            <Spinner size="xs" />
          </div>
        ) : (
          <div className="pb-1 pl-7">
            {columns.map((column) => (
              <button
                key={column.name}
                onClick={() => onInsert(column.name)}
                title={t("Insert into editor")}
                className="flex w-full items-center gap-2 rounded px-2 py-0.5 text-left hover:bg-gray-100"
              >
                <span className="truncate font-mono text-xs text-gray-600">
                  {column.name}
                </span>
                <span className="ml-auto shrink-0 rounded bg-gray-100 px-1 font-mono text-[10px] text-gray-500">
                  {column.type}
                </span>
              </button>
            ))}
          </div>
        ))}
    </div>
  );
};

const DataStudioSchemaBrowser = ({
  workspaceSlug,
  className,
  onInsert,
}: DataStudioSchemaBrowserProps) => {
  const { t } = useTranslation();
  const [search, setSearch] = useState("");

  const { data, loading } = useWorkspaceDataStudioSchemaQuery({
    variables: { workspaceSlug },
  });

  const tablePage = data?.workspace?.database?.tables;
  const tables = tablePage?.items ?? [];
  const hasMoreTables = (tablePage?.totalItems ?? 0) > tables.length;

  const shown = useMemo(() => {
    if (!search) {
      return tables;
    }
    const term = search.toLowerCase();
    return tables.filter((table) => table.name.toLowerCase().includes(term));
  }, [tables, search]);

  return (
    <div
      className={clsx(
        "flex flex-col overflow-hidden bg-gray-50/40 text-sm",
        className,
      )}
    >
      <div className="flex h-11 shrink-0 items-center gap-2 border-b border-gray-200 px-3">
        <CircleStackIcon className="h-4 w-4 text-gray-400" />
        <span className="font-medium text-gray-700">{t("Tables")}</span>
      </div>
      <div className="shrink-0 border-b border-gray-100 p-2">
        <input
          value={search}
          onChange={(event) => setSearch(event.target.value)}
          placeholder={t("Search…")}
          className="w-full rounded-md border border-gray-300 px-2 py-1 text-xs outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
        />
      </div>
      <div className="flex-1 overflow-auto p-1">
        {loading ? (
          <div className="flex justify-center py-6">
            <Spinner size="sm" />
          </div>
        ) : shown.length === 0 ? (
          <div className="px-2 py-4 text-center text-xs text-gray-400">
            {t("No tables")}
          </div>
        ) : (
          shown.map((table) => (
            <SchemaTableRow
              key={table.name}
              workspaceSlug={workspaceSlug}
              name={table.name}
              onInsert={onInsert}
            />
          ))
        )}
      </div>
      {hasMoreTables && (
        <div className="shrink-0 border-t border-gray-100 px-3 py-1.5 text-center text-[11px] text-gray-400">
          {t("Showing the first {{count}} tables.", {
            count: tables.length,
          })}
        </div>
      )}
    </div>
  );
};

DataStudioSchemaBrowser.queries = {
  schema: gql`
    query WorkspaceDataStudioSchema($workspaceSlug: String!) {
      workspace(slug: $workspaceSlug) {
        slug
        database {
          tables(page: 1, perPage: 100) {
            totalItems
            items {
              name
            }
          }
        }
      }
    }
  `,
  tableColumns: gql`
    query WorkspaceDataStudioTableColumns(
      $workspaceSlug: String!
      $table: String!
    ) {
      workspace(slug: $workspaceSlug) {
        slug
        database {
          table(name: $table) {
            name
            columns {
              name
              type
            }
          }
        }
      }
    }
  `,
};

export default DataStudioSchemaBrowser;

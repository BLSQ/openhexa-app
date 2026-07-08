import { gql } from "@apollo/client";
import {
  ChevronDownIcon,
  ChevronRightIcon,
  CircleStackIcon,
  MagnifyingGlassIcon,
  TableCellsIcon,
  XMarkIcon,
} from "@heroicons/react/24/outline";
import Spinner from "core/components/Spinner";
import clsx from "clsx";
import { useTranslation } from "next-i18next";
import { KeyboardEvent, useMemo, useRef, useState } from "react";
import { useWorkspaceDataStudioSchemaQuery } from "./DataStudioSchemaBrowser.generated";

type SchemaColumn = { name: string; type: string };

type DataStudioSchemaBrowserProps = {
  workspaceSlug: string;
  className?: string;
  onInsert(text: string): void;
};

type SchemaTableRowProps = {
  name: string;
  columns: SchemaColumn[];
  // Forces the row open regardless of the local toggle: used while searching so
  // tables that only match on a column name reveal that column.
  forceOpen: boolean;
  onInsert(text: string): void;
};

// The whole schema (tables + columns) is fetched in a single query, so columns
// are available up front and expanding a row is purely local — no round trip.
const SchemaTableRow = ({
  name,
  columns,
  forceOpen,
  onInsert,
}: SchemaTableRowProps) => {
  const { t } = useTranslation();
  const [open, setOpen] = useState(false);
  const isOpen = open || forceOpen;

  return (
    <div>
      <div className="group flex items-center rounded hover:bg-gray-100">
        <button
          onClick={() => setOpen((value) => !value)}
          className="flex flex-1 items-center gap-1.5 px-2 py-1.5 text-left"
        >
          {isOpen ? (
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
      {isOpen && (
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
      )}
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
  const [searchOpen, setSearchOpen] = useState(false);
  const searchRef = useRef<HTMLInputElement>(null);

  const { data, loading } = useWorkspaceDataStudioSchemaQuery({
    variables: { workspaceSlug },
  });

  const openSearch = () => {
    setSearchOpen(true);
    // Focus once the input has mounted.
    requestAnimationFrame(() => searchRef.current?.focus());
  };

  // Closing always clears the term so a hidden search never silently filters
  // the tree.
  const closeSearch = () => {
    setSearchOpen(false);
    setSearch("");
  };

  const onSearchKeyDown = (event: KeyboardEvent<HTMLInputElement>) => {
    if (event.key === "Escape") {
      closeSearch();
    }
  };

  const tablePage = data?.workspace?.database?.tables;
  const tables = tablePage?.items ?? [];
  const hasMoreTables = (tablePage?.totalItems ?? 0) > tables.length;

  const term = search.trim().toLowerCase();

  const shown = useMemo(() => {
    if (!term) {
      return tables;
    }
    return tables.filter(
      (table) =>
        table.name.toLowerCase().includes(term) ||
        table.columns.some((column) =>
          column.name.toLowerCase().includes(term),
        ),
    );
  }, [tables, term]);

  // Tables that match only through a column are force-expanded so the matching
  // column is visible without the user having to open every result manually.
  const forceOpen = useMemo(() => {
    if (!term) {
      return new Set<string>();
    }
    return new Set(
      tables
        .filter(
          (table) =>
            !table.name.toLowerCase().includes(term) &&
            table.columns.some((column) =>
              column.name.toLowerCase().includes(term),
            ),
        )
        .map((table) => table.name),
    );
  }, [tables, term]);

  return (
    <div
      className={clsx(
        "flex flex-col overflow-hidden bg-gray-50/40 text-sm",
        className,
      )}
    >
      <div className="flex h-11 shrink-0 items-center gap-2 border-b border-gray-200 px-3">
        {searchOpen ? (
          <>
            <MagnifyingGlassIcon className="h-4 w-4 shrink-0 text-gray-400" />
            <input
              ref={searchRef}
              value={search}
              onChange={(event) => setSearch(event.target.value)}
              onKeyDown={onSearchKeyDown}
              onBlur={() => {
                if (!search) {
                  setSearchOpen(false);
                }
              }}
              placeholder={`${t("Search tables & columns")}…`}
              className="min-w-0 flex-1 bg-transparent text-xs text-gray-700 outline-none placeholder:text-gray-400"
            />
            <button
              onClick={closeSearch}
              title={t("Close search")}
              className="shrink-0 rounded p-0.5 text-gray-400 hover:text-gray-700"
            >
              <XMarkIcon className="h-4 w-4" />
            </button>
          </>
        ) : (
          <>
            <CircleStackIcon className="h-4 w-4 shrink-0 text-gray-400" />
            <span className="font-medium text-gray-700">{t("Tables")}</span>
            <button
              onClick={openSearch}
              title={t("Search tables & columns")}
              className="ml-auto shrink-0 rounded p-0.5 text-gray-400 hover:text-gray-700"
            >
              <MagnifyingGlassIcon className="h-4 w-4" />
            </button>
          </>
        )}
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
              name={table.name}
              columns={table.columns}
              forceOpen={forceOpen.has(table.name)}
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
  // The full schema is fetched in one query: withColumns folds every table's
  // columns into the same round trip, and withCounts is disabled since the
  // browser never displays row counts (skipping the per-table COUNT(*)).
  schema: gql`
    query WorkspaceDataStudioSchema($workspaceSlug: String!) {
      workspace(slug: $workspaceSlug) {
        slug
        database {
          tables(
            page: 1
            perPage: 10000
            withColumns: true
            withCounts: false
          ) {
            totalItems
            items {
              name
              columns {
                name
                type
              }
            }
          }
        }
      }
    }
  `,
};

export default DataStudioSchemaBrowser;

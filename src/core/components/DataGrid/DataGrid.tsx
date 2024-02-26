/* eslint-disable react/jsx-key */
/* react-table already manages the key */

import { ChevronDownIcon, ChevronUpIcon } from "@heroicons/react/20/solid";
import clsx from "clsx";
import { useCheckboxColumn } from "core/hooks/useCheckboxColumn";
import usePrevious from "core/hooks/usePrevious";
import uniqueId from "lodash/uniqueId";
import isEqual from "lodash/isEqual";
import { useTranslation } from "next-i18next";
import React, {
  isValidElement,
  ReactNode,
  useCallback,
  useEffect,
  useMemo,
  useState,
} from "react";
import {
  Column as ReactTableColumn,
  PluginHook,
  SortingRule,
  useFlexLayout,
  usePagination,
  useRowSelect,
  useRowState,
  useSortBy,
  useTable,
} from "react-table";
import Pagination from "../Pagination";
import { Table, TableBody, TableCell, TableHead, TableRow } from "../Table";
import { BaseColumnProps } from "./BaseColumn";
import { CellContextProvider } from "./helpers";
import Overflow from "../Overflow";

export type { Cell, SortingRule } from "react-table";

export type Column<D extends object = any> = ReactTableColumn<D> & {
  Header: string | null;
  [key: string]: any;
};

interface IDataGridProps {
  children: ReactNode;
  data: object[];
  manualSortBy?: boolean;
  extraTableProps?: object;
  fixedLayout?: boolean;
  onSelectionChange?: (
    pageRows: object[],
    allIds: Record<string, boolean>,
  ) => void;
  fetchData?: (params: {
    page: number;
    pageSize: number;
    pageIndex: number;
    sortBy: SortingRule<object>[];
  }) => void;
  sortable?: boolean;
  totalItems?: number;
  idKey?: string;
  skipPageReset?: boolean;
  defaultPageSize?: number;
  className?: string;
  emptyLabel?: string;
  defaultSortBy?: SortingRule<object>[];
  pageSizeOptions?: number[];
  rowClassName?: string;
}

type DataGridProps = IDataGridProps;

function DataGrid(props: DataGridProps) {
  const { t } = useTranslation();
  const {
    children,
    data,
    rowClassName,
    fixedLayout = true,
    onSelectionChange,
    emptyLabel = t("No elements to display"),
    skipPageReset = false,
    fetchData,
    sortable = false,
    totalItems,
    idKey,
    className,
    pageSizeOptions,
    extraTableProps = {},
    defaultSortBy = [],
    defaultPageSize = 10,
  } = props;

  const [loading, setLoading] = useState(false);
  const hooks = useMemo(() => {
    const hooks: Array<PluginHook<{}>> = [
      useSortBy,
      usePagination,
      useRowSelect,
      useRowState,
    ];
    if (onSelectionChange) {
      hooks.push(useCheckboxColumn);
    }
    if (fixedLayout) {
      hooks.push(useFlexLayout);
    }
    return hooks;
  }, [onSelectionChange, fixedLayout]);

  const columns = useMemo(() => {
    const cols: Column[] = [];
    React.Children.map(children, (column) => {
      if (!isValidElement<BaseColumnProps>(column)) {
        throw new Error("Invalid column");
      }
      const def: any = {
        id: column.props.id ?? uniqueId("col"),
        Header: column.props.header ?? column.props.label ?? "",
        accessor: column.props.accessor ?? ((v: any) => v),
        className: column.props.className,
        hideLabel: column.props.hideLabel,
        Cell: () => React.cloneElement(column),
      };
      ["minWidth", "width", "maxWidth"].forEach((field) => {
        if (!fixedLayout && column.props[field]) {
          console.warn(
            `"${field}" is only used when DataGrid is in fixedLayout mode.`,
          );
        }
        if (column.props[field]) {
          def[field] = column.props[field];
        }
      });
      cols.push(def);
    });

    return cols;
  }, [children, fixedLayout]);

  const {
    getTableProps,
    getTableBodyProps,
    headerGroups,
    prepareRow,
    page,
    gotoPage,
    setPageSize,
    selectedFlatRows,
    state: { pageIndex, pageSize, sortBy, selectedRowIds },
  } = useTable(
    {
      columns,
      data,

      // Construct row ID
      getRowId(row, relativeIndex, parent) {
        const key = idKey ? (row as any)[idKey] : relativeIndex;
        return parent ? [parent.id, key].join(".") : key;
      },

      // Row selection
      autoResetSelectedRows: false,

      // Column width (used in fixedLayout configuration)
      defaultColumn: {
        minWidth: 30,
        width: 150,
        maxWidth: 400,
      },

      // Sort
      autoResetSortBy: false,
      disableSortBy: !sortable,
      manualSortBy: Boolean(fetchData),
      disableMultiSort: true,

      // Pagination
      manualPagination: Boolean(fetchData),
      autoResetPage: !skipPageReset,
      ...(Boolean(fetchData) ? { pageCount: -1 } : {}),

      // Initial state
      initialState: {
        sortBy: defaultSortBy,
        pageSize: defaultPageSize,
      },

      ...extraTableProps,
    },
    ...hooks,
  );

  const prevVariables = usePrevious({ pageIndex, sortBy, pageSize });

  useEffect(() => {
    if (onSelectionChange) {
      onSelectionChange(
        selectedFlatRows.map((x) => x.original),
        selectedRowIds,
      );
    }
  }, [selectedFlatRows, selectedRowIds, onSelectionChange]);

  const onFetchData = useCallback(
    async (params: any) => {
      if (!fetchData) {
        return;
      }
      setLoading(true);
      try {
        await fetchData(params);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    },
    [fetchData],
  );
  const onPaginationChange = useCallback(
    (page: number, perPage: number) => {
      if (perPage !== pageSize) {
        setPageSize(perPage);
      }
      if (page - 1 !== pageIndex) {
        gotoPage(page - 1);
      }
    },
    [gotoPage, setPageSize, pageIndex, pageSize],
  );

  useEffect(() => {
    if (
      !prevVariables ||
      isEqual(prevVariables, { pageIndex, sortBy, pageSize })
    ) {
      return;
    }
    onFetchData({ page: pageIndex + 1, pageIndex, pageSize, sortBy });
  }, [onFetchData, pageIndex, pageSize, sortBy, prevVariables]);

  return (
    <div className={className}>
      <Overflow horizontal gradientWidth="w-12">
        <Table
          {...getTableProps()}
          className={clsx(fixedLayout && "table-fixed")}
        >
          <TableHead>
            {headerGroups.map((headerGroup, i) => (
              <TableRow {...headerGroup.getHeaderGroupProps()}>
                {headerGroup.headers.map((column) => (
                  <TableCell
                    heading
                    className={column.headerClassName}
                    {...column.getHeaderProps(column.getSortByToggleProps())}
                  >
                    {column.hideLabel ? (
                      <span className="sr-only">{column.render("Header")}</span>
                    ) : (
                      <>
                        {column.render("Header")}
                        {column.isSorted && i === headerGroups.length - 1 && (
                          <div
                            className={clsx(
                              "ml-2 inline-block w-3 flex-none rounded bg-gray-200 text-gray-900 group-hover:bg-gray-300",
                            )}
                          >
                            {column.isSortedDesc ? (
                              <ChevronDownIcon
                                className="h-3 w-3"
                                aria-hidden="true"
                              />
                            ) : (
                              <ChevronUpIcon
                                className="h-3 w-3"
                                aria-hidden="true"
                              />
                            )}
                          </div>
                        )}
                      </>
                    )}
                  </TableCell>
                ))}
              </TableRow>
            ))}
          </TableHead>
          <TableBody {...getTableBodyProps()}>
            {page.map((row, i) => {
              prepareRow(row);
              return (
                <TableRow {...row.getRowProps()} className={rowClassName}>
                  {row.cells.map((cell) => (
                    <TableCell
                      {...cell.getCellProps({
                        className: cell.column.className,
                      })}
                    >
                      <CellContextProvider cell={cell}>
                        {cell.render("Cell")}
                      </CellContextProvider>
                    </TableCell>
                  ))}
                </TableRow>
              );
            })}
          </TableBody>
        </Table>
        {!page?.length && emptyLabel && (
          <div className="px-6 py-4 text-center text-sm italic text-gray-500">
            {emptyLabel}
          </div>
        )}
      </Overflow>

      {totalItems !== undefined && (
        <Pagination
          onChange={onPaginationChange}
          className="px-4"
          loading={loading}
          totalItems={totalItems}
          countItems={page.length}
          page={pageIndex + 1}
          perPage={pageSize}
          perPageOptions={pageSizeOptions}
        />
      )}
    </div>
  );
}

export default DataGrid;

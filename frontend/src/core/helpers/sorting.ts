import { SortingRule } from "react-table";
import { TFunction } from "next-i18next";

export interface SortOption<TOrderBy> {
  value: string;
  label: string;
  orderBy: TOrderBy;
}

export type ColumnToOrderByMap<TOrderBy> = Record<
  string,
  { asc: TOrderBy; desc: TOrderBy }
>;

export type OrderByToColumnMap = Record<string, { id: string; desc: boolean }>;

/**
 * Generates reverse mapping (OrderBy enum → column config) from column mapping.
 */
export function generateReverseMapping<TOrderBy>(
  mapping: ColumnToOrderByMap<TOrderBy>
): OrderByToColumnMap {
  const reverseMap: OrderByToColumnMap = {};

  for (const [columnId, { asc, desc }] of Object.entries(mapping)) {
    reverseMap[String(asc)] = { id: columnId, desc: false };
    reverseMap[String(desc)] = { id: columnId, desc: true };
  }

  return reverseMap;
}

/**
 * Creates bidirectional sorting utilities from a single column mapping.
 * Returns functions to convert between DataGrid sorting and GraphQL OrderBy enum.
 *
 * @example
 * const sorting = createSortingUtils({
 *   name: { asc: OrderBy.NameAsc, desc: OrderBy.NameDesc }
 * });
 *
 * const orderBy = sorting.convertDataGridSort(sortBy);
 * const defaultSort = sorting.convertToDataGridSort(orderBy);
 */
export function createSortingUtils<TOrderBy>(
  columnMapping: ColumnToOrderByMap<TOrderBy>
) {
  const reverseMapping = generateReverseMapping(columnMapping);

  return {
    columnMapping,
    reverseMapping,

    convertDataGridSort(sortBy: SortingRule<object>[]): TOrderBy | null {
      if (!sortBy || sortBy.length === 0) {
        return null;
      }

      const columnId = sortBy[0].id;
      const columnMap = columnMapping[columnId];

      if (!columnMap) {
        return null;
      }

      return sortBy[0].desc ? columnMap.desc : columnMap.asc;
    },

    convertToDataGridSort(orderBy: TOrderBy | null | undefined): SortingRule<object>[] {
      if (!orderBy) return [];

      const sortConfig = reverseMapping[String(orderBy)];
      if (!sortConfig) return [];

      return [sortConfig];
    },
  };
}

/**
 * Standalone converter: DataGrid sort → GraphQL OrderBy enum.
 * Prefer createSortingUtils() for bidirectional conversion.
 */
export function convertDataGridSortToGraphQL<TOrderBy>(
  sortBy: SortingRule<object>[],
  mapping: ColumnToOrderByMap<TOrderBy>
): TOrderBy | null {
  if (!sortBy || sortBy.length === 0) {
    return null;
  }

  const columnId = sortBy[0].id;
  const columnMapping = mapping[columnId];

  if (!columnMapping) {
    return null;
  }

  return sortBy[0].desc ? columnMapping.desc : columnMapping.asc;
}

/**
 * Creates localized sort options for dropdown/listbox from config.
 */
export function createSortOptions<TOrderBy>(
  options: Array<{
    value: string;
    orderBy: TOrderBy;
    labelKey: string;
  }>,
  t: TFunction<"common">
): SortOption<TOrderBy>[] {
  return options.map(({ value, orderBy, labelKey }) => ({
    value,
    orderBy,
    label: t(labelKey),
  }));
}

/**
 * Standalone converter: GraphQL OrderBy enum → DataGrid sort.
 * Prefer createSortingUtils() for bidirectional conversion.
 */
export function convertOrderByToDataGridSort<TOrderBy>(
  orderBy: TOrderBy | null | undefined,
  reverseMapping: Record<string, { id: string; desc: boolean }>
): SortingRule<object>[] {
  if (!orderBy) return [];

  const sortConfig = reverseMapping[String(orderBy)];
  if (!sortConfig) return [];

  return [sortConfig];
}

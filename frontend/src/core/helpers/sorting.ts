import { SortingRule } from "react-table";
import { TFunction } from "next-i18next";

/**
 * Generic sort option for any enum-based sorting
 */
export interface SortOption<TOrderBy> {
  value: string;
  label: string;
  orderBy: TOrderBy;
}

/**
 * Mapping from DataGrid column ID to enum values (asc/desc)
 */
export type ColumnToOrderByMap<TOrderBy> = Record<
  string,
  { asc: TOrderBy; desc: TOrderBy }
>;

/**
 * Reverse mapping from OrderBy enum to DataGrid column config
 */
export type OrderByToColumnMap = Record<string, { id: string; desc: boolean }>;

/**
 * Generates reverse mapping from column-to-orderBy mapping
 *
 * @example
 * const reverseMap = generateReverseMapping({
 *   name: { asc: OrderBy.NameAsc, desc: OrderBy.NameDesc }
 * });
 * // Returns: {
 * //   [OrderBy.NameAsc]: { id: "name", desc: false },
 * //   [OrderBy.NameDesc]: { id: "name", desc: true }
 * // }
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
 * Creates all sorting utilities for a given OrderBy enum
 *
 * @param columnMapping - Column ID to OrderBy enum mapping
 * @returns Object with all sorting utilities
 *
 * @example
 * const sorting = createSortingUtils({
 *   name: { asc: OrderBy.NameAsc, desc: OrderBy.NameDesc },
 *   createdAt: { asc: OrderBy.CreatedAtAsc, desc: OrderBy.CreatedAtDesc }
 * });
 *
 * // Use in component:
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
 * Converts react-table DataGrid sort to GraphQL OrderBy enum
 *
 * @param sortBy - The sorting rules from DataGrid
 * @param mapping - Column ID to OrderBy enum mapping
 * @returns The OrderBy enum value or null
 *
 * @example
 * const orderBy = convertDataGridSortToGraphQL(
 *   sortBy,
 *   {
 *     name: { asc: PipelineTemplateOrderBy.NameAsc, desc: PipelineTemplateOrderBy.NameDesc },
 *     createdAt: { asc: PipelineTemplateOrderBy.CreatedAtAsc, desc: PipelineTemplateOrderBy.CreatedAtDesc }
 *   }
 * );
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
 * Creates a list of sort options for a dropdown/listbox
 *
 * @param options - Array of option configurations
 * @returns Array of sort options
 *
 * @example
 * const options = createSortOptions([
 *   { value: "name-asc", orderBy: OrderBy.NameAsc, labelKey: "Name (A–Z)" },
 *   { value: "name-desc", orderBy: OrderBy.NameDesc, labelKey: "Name (Z–A)" }
 * ], t);
 */
export function createSortOptions<TOrderBy>(
  options: Array<{
    value: string;
    orderBy: TOrderBy;
    labelKey: string;
  }>,
  t: TFunction
): SortOption<TOrderBy>[] {
  return options.map(({ value, orderBy, labelKey }) => ({
    value,
    orderBy,
    label: t(labelKey),
  }));
}

/**
 * Converts OrderBy enum back to DataGrid sorting format
 * Used for setting defaultSortBy in DataGrid
 *
 * @param orderBy - The OrderBy enum value
 * @param reverseMapping - OrderBy enum to column ID and direction mapping
 * @returns DataGrid sorting rule or empty array
 *
 * @example
 * const defaultSortBy = convertOrderByToDataGridSort(
 *   PipelineTemplateOrderBy.NameDesc,
 *   {
 *     [PipelineTemplateOrderBy.NameAsc]: { id: "name", desc: false },
 *     [PipelineTemplateOrderBy.NameDesc]: { id: "name", desc: true }
 *   }
 * );
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

import { SortingRule } from "react-table";

export interface SortOption<TOrderBy> {
  value: string;
  label: string;
  orderBy: TOrderBy;
}

export type ColumnToOrderByMap<TOrderBy> = Record<
  string,
  { asc: TOrderBy; desc: TOrderBy }
>;

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
  return {
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

    convertToDataGridSort(
      orderBy: TOrderBy | null | undefined
    ): SortingRule<object>[] {
      if (!orderBy) return [];

      // Find matching column by iterating through mapping
      for (const [columnId, { asc, desc }] of Object.entries(columnMapping)) {
        if (asc === orderBy) {
          return [{ id: columnId, desc: false }];
        }
        if (desc === orderBy) {
          return [{ id: columnId, desc: true }];
        }
      }

      return [];
    },
  };
}

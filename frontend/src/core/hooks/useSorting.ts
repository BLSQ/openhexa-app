import { useState } from "react";
import { SortDirection } from "graphql/types";

export interface SortOption<TField = string> {
  value: string;
  label: string;
  field: TField;
  direction: SortDirection;
}

export interface UseSortingOptions<TField = string> {
  defaultSort: SortOption<TField>;
  options: SortOption<TField>[];
}

export interface UseSortingReturn<TField = string> {
  sortOrder: SortOption<TField>;
  setSortOrder: (option: SortOption<TField>) => void;
  sortOptions: SortOption<TField>[];
  getSortInput: () => { field: TField; direction: SortDirection };
}

/**
 * Generic hook for managing sorting state.
 *
 * @example
 * const sorting = useSorting({
 *   defaultSort: { value: "name-asc", field: "NAME", direction: SortDirection.Asc, label: "Name (A-Z)" },
 *   options: [
 *     { value: "name-asc", field: "NAME", direction: SortDirection.Asc, label: "Name (A-Z)" },
 *     { value: "name-desc", field: "NAME", direction: SortDirection.Desc, label: "Name (Z-A)" },
 *   ]
 * });
 *
 * // In GraphQL query:
 * variables: {
 *   sort: sorting.getSortInput()
 * }
 */
export function useSorting<TField = string>({
  defaultSort,
  options,
}: UseSortingOptions<TField>): UseSortingReturn<TField> {
  const [sortOrder, setSortOrder] = useState<SortOption<TField>>(defaultSort);

  const getSortInput = () => ({
    field: sortOrder.field,
    direction: sortOrder.direction,
  });

  return {
    sortOrder,
    setSortOrder,
    sortOptions: options,
    getSortInput,
  };
}

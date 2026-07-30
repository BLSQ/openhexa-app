import { createSortingUtils } from "core/helpers/sorting";
import { SavedQueryOrderBy } from "graphql/types";

export const DEFAULT_SAVED_QUERY_ORDER_BY = SavedQueryOrderBy.UpdatedAtDesc;

// Keys must match the `id` of the corresponding DataGrid column: react-table
// reports the sorted column by id and this map turns it into the GraphQL enum.
export const savedQuerySorting = createSortingUtils({
  name: {
    asc: SavedQueryOrderBy.NameAsc,
    desc: SavedQueryOrderBy.NameDesc,
  },
  updatedAt: {
    asc: SavedQueryOrderBy.UpdatedAtAsc,
    desc: SavedQueryOrderBy.UpdatedAtDesc,
  },
});

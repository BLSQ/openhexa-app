import { gql, useQuery } from "@apollo/client";
import SearchResult from "catalog/features/SearchResult";
import { SearchResult_ResultFragment } from "catalog/features/SearchResult.generated";
import { SearchQueryQuery } from "./useSearch.generated";

export type UseSearchOptions = {
  query?: string;
  datasourceIds?: string[];
  types?: string[];
  page?: number;
  perPage?: number;
};

function useSearch(options: UseSearchOptions) {
  const { query, page, perPage, datasourceIds, types } = options;
  const { data, loading, previousData } = useQuery<SearchQueryQuery>(
    gql`
      query SearchQuery(
        $query: String
        $types: [String!]
        $datasourceIds: [String!]
        $page: Int
        $perPage: Int
      ) {
        search(
          query: $query
          datasourceIds: $datasourceIds
          types: $types
          page: $page
          perPage: $perPage
        ) {
          results {
            ...SearchResult_result
          }
          types {
            value
            label
          }
        }
      }
      ${SearchResult.fragments.result}
    `,
    {
      variables: { query, page, perPage, datasourceIds, types },
    }
  );

  const results = (data || previousData)?.search.results;
  return {
    results: results as SearchResult_ResultFragment[] | undefined,
    types: (data || previousData)?.search.types,
    loading,
  } as const;
}

export default useSearch;

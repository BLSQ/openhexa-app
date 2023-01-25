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
  skip?: boolean;
};

function useSearch(options: UseSearchOptions) {
  const { query, page, perPage, datasourceIds, types, skip = false } = options;
  const { data, loading, previousData } = useQuery<SearchQueryQuery>(
    gql`
      query SearchQuery(
        $query: String
        $types: [String!]
        $datasourceIds: [UUID!]
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
      skip,
    }
  );
  if (skip) {
    return { results: undefined, types: undefined, loading: false };
  }

  const results = (data || previousData)?.search.results;
  return {
    results: results as SearchResult_ResultFragment[] | undefined,
    types: (data || previousData)?.search.types,
    loading: loading ?? false,
  } as const;
}

export default useSearch;

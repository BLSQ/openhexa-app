import { useQuery } from "@apollo/client";
import { renderHook } from "@testing-library/react";
import useSearch from "./useSearch";

jest.mock("@apollo/client", () => ({
  __esModule: true,
  useQuery: jest.fn(),
  gql: jest.fn(() => "GQL"),
}));
const useQueryMock = useQuery as jest.Mock;

describe.only("useSearch", () => {
  it("returns empty lists when skipped", () => {
    useQueryMock.mockReturnValue([]);
    const { result } = renderHook(() =>
      useSearch({ query: "QUERY", skip: true }),
    );

    expect(useQueryMock).toHaveBeenCalledWith("GQL", {
      skip: true,
      variables: {
        query: "QUERY",
        types: undefined,
        datasourceIds: undefined,
        page: undefined,
        perPage: undefined,
      },
    });

    expect(result.current).toEqual({
      loading: false,
      results: undefined,
      types: undefined,
    });
  });

  it("returns results", () => {
    useQueryMock.mockReturnValue({
      loading: true,
      data: {
        search: {
          results: [],
          types: [{ value: "1", label: "Label of type 1" }],
        },
      },
    });
    const { result } = renderHook(() =>
      useSearch({ query: "QUERY", page: 2, types: ["1"] }),
    );

    expect(useQueryMock).toHaveBeenCalledWith("GQL", {
      skip: false,
      variables: {
        query: "QUERY",
        types: ["1"],
        datasourceIds: undefined,
        page: 2,
        perPage: undefined,
      },
    });

    expect(result.current).toEqual({
      loading: true,
      results: [],
      types: [{ value: "1", label: "Label of type 1" }],
    });
  });
});

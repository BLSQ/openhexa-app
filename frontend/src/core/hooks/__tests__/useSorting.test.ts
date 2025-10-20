import { renderHook, act } from "@testing-library/react";
import { useSorting, SortOption } from "../useSorting";
import { SortDirection } from "graphql/types";

describe("useSorting", () => {
  const mockSortOptions: SortOption<string>[] = [
    {
      value: "name-asc",
      label: "Name (A-Z)",
      field: "NAME",
      direction: SortDirection.Asc,
    },
    {
      value: "name-desc",
      label: "Name (Z-A)",
      field: "NAME",
      direction: SortDirection.Desc,
    },
    {
      value: "date-desc",
      label: "Date (Newest)",
      field: "CREATED_AT",
      direction: SortDirection.Desc,
    },
  ];

  it("should initialize with default sort", () => {
    const { result } = renderHook(() =>
      useSorting({
        defaultSort: mockSortOptions[0],
        options: mockSortOptions,
      })
    );

    expect(result.current.sortOrder).toEqual(mockSortOptions[0]);
    expect(result.current.sortOptions).toEqual(mockSortOptions);
  });

  it("should update sort order", () => {
    const { result } = renderHook(() =>
      useSorting({
        defaultSort: mockSortOptions[0],
        options: mockSortOptions,
      })
    );

    act(() => {
      result.current.setSortOrder(mockSortOptions[1]);
    });

    expect(result.current.sortOrder).toEqual(mockSortOptions[1]);
  });

  it("should return correct sort input for GraphQL", () => {
    const { result } = renderHook(() =>
      useSorting({
        defaultSort: mockSortOptions[0],
        options: mockSortOptions,
      })
    );

    const sortInput = result.current.getSortInput();

    expect(sortInput).toEqual({
      field: "NAME",
      direction: SortDirection.Asc,
    });
  });

  it("should update sort input after sort order change", () => {
    const { result } = renderHook(() =>
      useSorting({
        defaultSort: mockSortOptions[0],
        options: mockSortOptions,
      })
    );

    act(() => {
      result.current.setSortOrder(mockSortOptions[2]);
    });

    const sortInput = result.current.getSortInput();

    expect(sortInput).toEqual({
      field: "CREATED_AT",
      direction: SortDirection.Desc,
    });
  });

  it("should work with generic field types", () => {
    enum CustomSortField {
      CustomFieldA = "CUSTOM_A",
      CustomFieldB = "CUSTOM_B",
    }

    const customOptions: SortOption<CustomSortField>[] = [
      {
        value: "custom-a",
        label: "Custom A",
        field: CustomSortField.CustomFieldA,
        direction: SortDirection.Asc,
      },
      {
        value: "custom-b",
        label: "Custom B",
        field: CustomSortField.CustomFieldB,
        direction: SortDirection.Desc,
      },
    ];

    const { result } = renderHook(() =>
      useSorting({
        defaultSort: customOptions[0],
        options: customOptions,
      })
    );

    expect(result.current.sortOrder.field).toBe(CustomSortField.CustomFieldA);

    act(() => {
      result.current.setSortOrder(customOptions[1]);
    });

    expect(result.current.sortOrder.field).toBe(CustomSortField.CustomFieldB);
    expect(result.current.getSortInput()).toEqual({
      field: CustomSortField.CustomFieldB,
      direction: SortDirection.Desc,
    });
  });

  it("should maintain sort options reference", () => {
    const { result } = renderHook(() =>
      useSorting({
        defaultSort: mockSortOptions[0],
        options: mockSortOptions,
      })
    );

    const initialOptions = result.current.sortOptions;

    act(() => {
      result.current.setSortOrder(mockSortOptions[1]);
    });

    expect(result.current.sortOptions).toBe(initialOptions);
  });
});

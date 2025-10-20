import { SortOption } from "core/hooks/useSorting";
import { SortDirection, PipelineTemplateSortField } from "graphql/types";
import { SortingRule } from "react-table";
import { TFunction } from "next-i18next";

export const COLUMN_TO_FIELD_MAP: Record<string, PipelineTemplateSortField> = {
  name: PipelineTemplateSortField.Name,
  createdAt: PipelineTemplateSortField.CreatedAt,
  popularity: PipelineTemplateSortField.PipelinesCount,
};

export function convertDataGridSortToGraphQL(
  sortBy: SortingRule<object>[]
): { field: PipelineTemplateSortField; direction: SortDirection } | null {
  if (!sortBy || sortBy.length === 0) {
    return null;
  }

  const columnId = sortBy[0].id;
  const field = COLUMN_TO_FIELD_MAP[columnId];

  if (!field) {
    return null;
  }

  return {
    field,
    direction: sortBy[0].desc ? SortDirection.Desc : SortDirection.Asc,
  };
}

export function getTemplateSortOptions(
  t: TFunction
): SortOption<PipelineTemplateSortField>[] {
  return [
    {
      value: "popularity-desc",
      field: PipelineTemplateSortField.PipelinesCount,
      direction: SortDirection.Desc,
      label: t("Popularity (Most used)"),
    },
    {
      value: "created-desc",
      field: PipelineTemplateSortField.CreatedAt,
      direction: SortDirection.Desc,
      label: t("Date Created (Newest)"),
    },
    {
      value: "created-asc",
      field: PipelineTemplateSortField.CreatedAt,
      direction: SortDirection.Asc,
      label: t("Date Created (Oldest)"),
    },
    {
      value: "popularity-asc",
      field: PipelineTemplateSortField.PipelinesCount,
      direction: SortDirection.Asc,
      label: t("Popularity (Least used)"),
    },
    {
      value: "name-asc",
      field: PipelineTemplateSortField.Name,
      direction: SortDirection.Asc,
      label: t("Name (A–Z)"),
    },
    {
      value: "name-desc",
      field: PipelineTemplateSortField.Name,
      direction: SortDirection.Desc,
      label: t("Name (Z–A)"),
    },
  ];
}

import { SortingRule } from "react-table";
import { TFunction } from "next-i18next";
import { PipelineTemplateOrderBy } from "graphql/types";

export interface TemplateSortOption {
  value: string;
  label: string;
  orderBy: PipelineTemplateOrderBy;
}

export const COLUMN_TO_ORDER_BY_MAP: Record<string, { asc: PipelineTemplateOrderBy; desc: PipelineTemplateOrderBy }> = {
  name: {
    asc: PipelineTemplateOrderBy.NameAsc,
    desc: PipelineTemplateOrderBy.NameDesc,
  },
  createdAt: {
    asc: PipelineTemplateOrderBy.CreatedAtAsc,
    desc: PipelineTemplateOrderBy.CreatedAtDesc,
  },
  popularity: {
    asc: PipelineTemplateOrderBy.PipelinesCountAsc,
    desc: PipelineTemplateOrderBy.PipelinesCountDesc,
  },
};

export function convertDataGridSortToGraphQL(
  sortBy: SortingRule<object>[]
): PipelineTemplateOrderBy | null {
  if (!sortBy || sortBy.length === 0) {
    return null;
  }

  const columnId = sortBy[0].id;
  const mapping = COLUMN_TO_ORDER_BY_MAP[columnId];

  if (!mapping) {
    return null;
  }

  return sortBy[0].desc ? mapping.desc : mapping.asc;
}

export function getTemplateSortOptions(
  t: TFunction
): TemplateSortOption[] {
  return [
    {
      value: "popularity-desc",
      orderBy: PipelineTemplateOrderBy.PipelinesCountDesc,
      label: t("Popularity (Most used)"),
    },
    {
      value: "created-desc",
      orderBy: PipelineTemplateOrderBy.CreatedAtDesc,
      label: t("Date Created (Newest)"),
    },
    {
      value: "created-asc",
      orderBy: PipelineTemplateOrderBy.CreatedAtAsc,
      label: t("Date Created (Oldest)"),
    },
    {
      value: "popularity-asc",
      orderBy: PipelineTemplateOrderBy.PipelinesCountAsc,
      label: t("Popularity (Least used)"),
    },
    {
      value: "name-asc",
      orderBy: PipelineTemplateOrderBy.NameAsc,
      label: t("Name (A–Z)"),
    },
    {
      value: "name-desc",
      orderBy: PipelineTemplateOrderBy.NameDesc,
      label: t("Name (Z–A)"),
    },
  ];
}

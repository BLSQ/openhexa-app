import { TFunction } from "next-i18next";
import { PipelineTemplateOrderBy } from "graphql/types";
import {
  SortOption,
  createSortingUtils,
  createSortOptions,
} from "core/helpers/sorting";

export type TemplateSortOption = SortOption<PipelineTemplateOrderBy>;

export const templateSorting = createSortingUtils({
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
});

export function getTemplateSortOptions(
  t: TFunction
): SortOption<PipelineTemplateOrderBy>[] {
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
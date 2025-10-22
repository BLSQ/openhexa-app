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
): TemplateSortOption[] {
  return createSortOptions(
    [
      { value: "popularity-desc", orderBy: PipelineTemplateOrderBy.PipelinesCountDesc, labelKey: "Popularity (Most used)" },
      { value: "created-desc", orderBy: PipelineTemplateOrderBy.CreatedAtDesc, labelKey: "Date Created (Newest)" },
      { value: "created-asc", orderBy: PipelineTemplateOrderBy.CreatedAtAsc, labelKey: "Date Created (Oldest)" },
      { value: "popularity-asc", orderBy: PipelineTemplateOrderBy.PipelinesCountAsc, labelKey: "Popularity (Least used)" },
      { value: "name-asc", orderBy: PipelineTemplateOrderBy.NameAsc, labelKey: "Name (A–Z)" },
      { value: "name-desc", orderBy: PipelineTemplateOrderBy.NameDesc, labelKey: "Name (Z–A)" },
    ],
    t
  );
}

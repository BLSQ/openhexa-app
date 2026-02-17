import { i18n } from "next-i18next";
import { PipelineOrderBy, PipelineTemplateOrderBy } from "graphql/types";
import { SortOption, createSortingUtils } from "core/helpers/sorting";

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

export function getTemplateSortOptions(): SortOption<PipelineTemplateOrderBy>[] {
  return [
    {
      value: "popularity-desc",
      orderBy: PipelineTemplateOrderBy.PipelinesCountDesc,
      label: i18n!.t("Popularity (Most used)"),
    },
    {
      value: "popularity-asc",
      orderBy: PipelineTemplateOrderBy.PipelinesCountAsc,
      label: i18n!.t("Popularity (Least used)"),
    },
    {
      value: "created-desc",
      orderBy: PipelineTemplateOrderBy.CreatedAtDesc,
      label: i18n!.t("Date Created (Newest)"),
    },
    {
      value: "created-asc",
      orderBy: PipelineTemplateOrderBy.CreatedAtAsc,
      label: i18n!.t("Date Created (Oldest)"),
    },
    {
      value: "name-asc",
      orderBy: PipelineTemplateOrderBy.NameAsc,
      label: i18n!.t("Name (A–Z)"),
    },
    {
      value: "name-desc",
      orderBy: PipelineTemplateOrderBy.NameDesc,
      label: i18n!.t("Name (Z–A)"),
    },
  ];
}

export type PipelineSortOption = SortOption<PipelineOrderBy>;

export const pipelineSorting = createSortingUtils({
  name: {
    asc: PipelineOrderBy.NameAsc,
    desc: PipelineOrderBy.NameDesc,
  },
  lastRunDate: {
    asc: PipelineOrderBy.LastRunDateAsc,
    desc: PipelineOrderBy.LastRunDateDesc,
  },
});

export function getPipelineSortOptions(): SortOption<PipelineOrderBy>[] {
  return [
    {
      value: "name-asc",
      orderBy: PipelineOrderBy.NameAsc,
      label: i18n!.t("Name (A–Z)"),
    },
    {
      value: "name-desc",
      orderBy: PipelineOrderBy.NameDesc,
      label: i18n!.t("Name (Z–A)"),
    },
    {
      value: "lastrundate-asc",
      orderBy: PipelineOrderBy.LastRunDateAsc,
      label: i18n!.t("Last Run Date (Newest)"),
    },
    {
      value: "lastrundate-desc",
      orderBy: PipelineOrderBy.LastRunDateDesc,
      label: i18n!.t("Last Run Date (Oldest)"),
    },
  ];
}

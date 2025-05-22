import {
  BoltIcon,
  CircleStackIcon,
  DocumentIcon,
  FolderOpenIcon,
  QuestionMarkCircleIcon,
  Square2StackIcon,
  StarIcon,
} from "@heroicons/react/24/outline";
import { DatabaseTablesPageFragment } from "./DatabaseTableResultTable.generated";
import { PipelinesPageFragment } from "./PipelineResultTable.generated";
import { PipelineTemplatesPageFragment } from "./PipelineTemplateResultTable.generated";
import { DatasetsPageFragment } from "./DatasetResultTable.generated";
import { FilesPageFragment } from "./FileResultTable.generated";
import { FileType } from "graphql/types";
import { Url } from "next-router-mock";

export type Item =
  | DatabaseTablesPageFragment["items"][0]
  | PipelinesPageFragment["items"][0]
  | PipelineTemplatesPageFragment["items"][0]
  | DatasetsPageFragment["items"][0]
  | FilesPageFragment["items"][0];

export type TypeName = Exclude<Item["__typename"], undefined>;

const typeIconMap: Record<TypeName, typeof CircleStackIcon> = {
  DatabaseTableResult: CircleStackIcon,
  PipelineResult: BoltIcon,
  PipelineTemplateResult: StarIcon,
  DatasetResult: Square2StackIcon,
  FileResult: FolderOpenIcon,
};

export const getTypeIcon = (
  typeName: TypeName,
  type?: FileType,
): typeof BoltIcon => {
  if (typeName === "FileResult") {
    return type === FileType.Directory ? FolderOpenIcon : DocumentIcon;
  }
  return typeIconMap[typeName] || QuestionMarkCircleIcon;
};

const labelMap = (t: (key: string) => string): Record<TypeName, string> => ({
  DatabaseTableResult: t("Table"),
  PipelineResult: t("Pipeline"),
  PipelineTemplateResult: t("Pipeline Template"),
  DatasetResult: t("Dataset"),
  FileResult: t("File"),
});

export const getLabel = (
  typeName: TypeName,
  t: (key: string) => string,
  type?: FileType,
): string => {
  if (typeName === "FileResult") {
    return type === FileType.Directory ? t("Directory") : t("File");
  }
  return labelMap(t)[typeName] ?? t("Unknown");
};

export const getObject = (item: Item): any => {
  switch (item.__typename) {
    case "DatabaseTableResult":
      return item.databaseTable;
    case "PipelineResult":
      return item.pipeline;
    case "PipelineTemplateResult":
      return item.pipelineTemplate;
    case "DatasetResult":
      return item.dataset;
    case "FileResult":
      return item.file;
    default:
      return null;
  }
};

export const getWorkspace = (item: Item): any => {
  if (
    item.__typename === "DatabaseTableResult" ||
    item.__typename === "FileResult"
  ) {
    return item.workspace;
  }
  return getObject(item)?.workspace ?? null;
};

const getUrlName = (typeName: TypeName): string => {
  switch (typeName) {
    case "DatasetResult":
      return "datasets";
    case "PipelineResult":
      return "pipelines";
    case "DatabaseTableResult":
      return "databases";
    case "PipelineTemplateResult":
      return "templates";
    case "FileResult":
      return "files";
    default:
      return "";
  }
};

const getUrlId = (item: Item): string => {
  const object = getObject(item);
  if (!object) return "";
  switch (item.__typename) {
    case "DatasetResult":
      return object.slug;
    case "DatabaseTableResult":
      return object.name;
    case "PipelineResult":
    case "PipelineTemplateResult":
      return object.code;
    case "FileResult":
      return object.name;
    default:
      return "";
  }
};

// TODO : logo

export const getUrl = (item: Item, currentWorkspaceSlug?: string): Url => {
  const workspaceSlug =
    item.__typename === "PipelineTemplateResult" && currentWorkspaceSlug
      ? currentWorkspaceSlug
      : getWorkspace(item).slug;
  if (!item.__typename) return "";
  if (item.__typename === "FileResult") {
    const object = getObject(item);
    let urlName = object.name.endsWith(".ipynb")
      ? "notebooks"
      : getUrlName(item.__typename);
    const parentPath = object.path
      .replace(/\/$/, "") // rstrip trailing slash if any
      .split("/")
      .slice(1, -1)
      .map(encodeURIComponent);
    const objectPath = [...parentPath, encodeURIComponent(object.name)];
    const query =
      object.type === FileType.File
        ? { q: object.name }
        : object.name.endsWith(".ipynb")
          ? { open: objectPath.join("/") }
          : {};
    return {
      pathname: [
        "",
        "workspaces",
        encodeURIComponent(workspaceSlug),
        urlName,
        ...(object.type === FileType.Directory ? objectPath : parentPath),
      ].join("/"),
      query,
    };
  }
  return `/workspaces/${encodeURIComponent(workspaceSlug)}/${getUrlName(item.__typename)}/${getUrlId(item)}`;
};

export const getItems = (data: { items?: any[] } | undefined): any[] => {
  return data?.items || [];
};

export const getTotalItems = (
  data: { totalItems?: number } | undefined,
): number => {
  return data?.totalItems || 0;
};

export const hasNextPage = (
  data: { pageNumber?: number; totalPages?: number } | undefined,
): boolean => {
  return (data?.pageNumber || 0) < (data?.totalPages || 0);
};

export const hasPreviousPage = (
  data: { pageNumber?: number } | undefined,
): boolean => {
  return (data?.pageNumber || 1) > 1;
};

import { WebappOperationScope } from "graphql/types";

// HEXA-1815: write access is being removed from the web app API. These scopes
// can no longer be enabled from the UI, but a web app that already has one
// keeps its toggle so existing apps are not broken.
export const LEGACY_SCOPES: WebappOperationScope[] = [
  WebappOperationScope.FilesWrite,
  WebappOperationScope.DatasetsWrite,
];

export function getScopeDescriptions(t: (key: string) => string) {
  return {
    [WebappOperationScope.PipelinesRead]: {
      label: t("Read pipelines"),
      description: t("Access pipeline metadata, versions, and run details"),
    },
    [WebappOperationScope.PipelinesRun]: {
      label: t("Run pipelines"),
      description: t("Start and stop pipeline runs"),
    },
    [WebappOperationScope.FilesRead]: {
      label: t("Read files"),
      description: t("Access workspace files and download objects"),
    },
    [WebappOperationScope.FilesWrite]: {
      label: t("Write files"),
      description: t("Upload, create, and delete workspace files"),
    },
    [WebappOperationScope.DatasetsRead]: {
      label: t("Read datasets"),
      description: t("Access workspace datasets, versions, and links"),
    },
    [WebappOperationScope.DatasetsWrite]: {
      label: t("Write datasets"),
      description: t("Create, update, and delete datasets and versions"),
    },
    [WebappOperationScope.UserRead]: {
      label: t("Read user info"),
      description: t("Access current user details and workspace role"),
    },
    [WebappOperationScope.DatabaseRead]: {
      label: t("Read database"),
      description: t(
        "Run saved queries against the workspace database. The SQL stays hidden from the web app.",
      ),
    },
  };
}

type ScopeGroup = {
  title: string;
  scopes: WebappOperationScope[];
};

export function getScopeGroups(t: (key: string) => string): ScopeGroup[] {
  return [
    {
      title: t("Datasets"),
      scopes: [
        WebappOperationScope.DatasetsRead,
        WebappOperationScope.DatasetsWrite,
      ],
    },
    {
      title: t("Pipelines"),
      scopes: [
        WebappOperationScope.PipelinesRead,
        WebappOperationScope.PipelinesRun,
      ],
    },
    {
      title: t("Files"),
      scopes: [WebappOperationScope.FilesRead, WebappOperationScope.FilesWrite],
    },
    {
      title: t("Database"),
      scopes: [WebappOperationScope.DatabaseRead],
    },
    {
      title: t("User"),
      scopes: [WebappOperationScope.UserRead],
    },
  ];
}

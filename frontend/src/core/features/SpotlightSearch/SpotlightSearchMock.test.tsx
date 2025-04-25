import {
  GetWorkspacesDocument,
  SearchDatabaseTablesDocument,
  SearchDatasetsDocument,
  SearchFilesDocument,
  SearchPipelinesDocument,
  SearchPipelineTemplatesDocument,
} from "./SpotlightSearch.generated";

export const mocks = [
  {
    request: {
      query: GetWorkspacesDocument,
      variables: { perPage: 1000 },
    },
    result: {
      data: {
        workspaces: {
          totalItems: 2,
          items: [
            {
              slug: "test-workspace",
              name: "Test Workspace",
              countries: [{ code: "US", __typename: "Country" }],
              __typename: "Workspace",
            },
            {
              slug: "test-workspace2",
              name: "Test Workspace2",
              countries: [{ code: "US", __typename: "Country" }],
              __typename: "Workspace",
            },
          ],
          __typename: "WorkspaceConnection",
        },
      },
    },
  },
  {
    request: {
      query: SearchDatasetsDocument,
      variables: {
        query: "test query",
        workspaceSlugs: ["test-workspace"],
        page: 1,
        perPage: 15,
      },
    },
    result: {
      data: {
        datasets: {
          items: [
            {
              dataset: {
                id: "1",
                slug: "test-dataset",
                name: "Test Dataset",
                description: "A test dataset",
                workspace: {
                  slug: "test-workspace",
                  name: "Test Workspace",
                  countries: [{ code: "US", __typename: "Country" }],
                  __typename: "Workspace",
                },
                createdBy: {
                  id: "1",
                  displayName: "Test User",
                  avatar: {
                    initials: "TU",
                    color: "blue",
                    __typename: "Avatar",
                  },
                  __typename: "User",
                },
                updatedAt: "2023-01-01T00:00:00Z",
                __typename: "Dataset",
              },
              score: 1.0,
              __typename: "DatasetResult",
            },
          ],
          totalItems: 1,
          pageNumber: 1,
          totalPages: 1,
          __typename: "DatasetResultPage",
        },
      },
    },
  },
  {
    request: {
      query: SearchPipelinesDocument,
      variables: {
        query: "test query",
        workspaceSlugs: ["test-workspace"],
        page: 1,
        perPage: 15,
      },
    },
    result: {
      data: {
        pipelines: {
          items: [
            {
              pipeline: {
                id: "1",
                code: "test-pipeline",
                name: "Test Pipeline",
                description: "A test pipeline",
                updatedAt: "2023-01-01T00:00:00Z",
                workspace: {
                  slug: "test-workspace",
                  name: "Test Workspace",
                  countries: [{ code: "US", __typename: "Country" }],
                  __typename: "Workspace",
                },
                lastRuns: {
                  items: [
                    {
                      id: "1",
                      status: "SUCCESS",
                      __typename: "PipelineRun",
                    },
                  ],
                  __typename: "PipelineRunConnection",
                },
                __typename: "Pipeline",
              },
              score: 1.0,
              __typename: "PipelineResult",
            },
          ],
          totalItems: 1,
          pageNumber: 1,
          totalPages: 1,
          __typename: "PipelineResultPage",
        },
      },
    },
  },
  {
    request: {
      query: SearchPipelineTemplatesDocument,
      variables: {
        query: "test query",
        workspaceSlugs: ["test-workspace"],
        page: 1,
        perPage: 15,
      },
    },
    result: {
      data: {
        pipelineTemplates: {
          items: [
            {
              pipelineTemplate: {
                id: "1",
                code: "test-template",
                name: "Test Template",
                description: "A test template",
                updatedAt: "2023-01-01T00:00:00Z",
                workspace: {
                  slug: "test-workspace",
                  name: "Test Workspace",
                  countries: [{ code: "US", __typename: "Country" }],
                  __typename: "Workspace",
                },
                currentVersion: {
                  id: "1",
                  versionNumber: "1.0",
                  __typename: "PipelineTemplateVersion",
                },
                __typename: "PipelineTemplate",
              },
              score: 1.0,
              __typename: "PipelineTemplateResult",
            },
          ],
          totalItems: 1,
          pageNumber: 1,
          totalPages: 1,
          __typename: "PipelineTemplateResultPage",
        },
      },
    },
  },
  {
    request: {
      query: SearchDatabaseTablesDocument,
      variables: {
        query: "test query",
        workspaceSlugs: ["test-workspace"],
        page: 1,
        perPage: 15,
      },
    },
    result: {
      data: {
        databaseTables: {
          items: [
            {
              databaseTable: {
                name: "Test Table",
                count: 42,
                __typename: "DatabaseTable",
              },
              score: 1.0,
              workspace: {
                slug: "test-workspace",
                name: "Test Workspace",
                countries: [{ code: "US", __typename: "Country" }],
                __typename: "Workspace",
              },
              __typename: "DatabaseTableResult",
            },
          ],
          totalItems: 1,
          pageNumber: 1,
          totalPages: 1,
          __typename: "DatabaseTableResultPage",
        },
      },
    },
  },
  {
    request: {
      query: SearchFilesDocument,
      variables: {
        query: "test query",
        workspaceSlugs: ["test-workspace"],
        page: 1,
        perPage: 15,
      },
    },
    result: {
      data: {
        files: {
          items: [
            {
              file: {
                name: "Test File",
                path: "/test/path",
                size: 1024,
                updated: "2023-01-01T00:00:00Z",
                type: "text",
                __typename: "File",
              },
              score: 1.0,
              workspace: {
                slug: "test-workspace",
                name: "Test Workspace",
                countries: [{ code: "US", __typename: "Country" }],
                __typename: "Workspace",
              },
              __typename: "FileResult",
            },
          ],
          totalItems: 1,
          pageNumber: 1,
          totalPages: 1,
          __typename: "FileResultPage",
        },
      },
    },
  },
];

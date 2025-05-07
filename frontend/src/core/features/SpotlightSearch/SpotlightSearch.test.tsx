import React from "react";
import { render, fireEvent, screen, waitFor } from "@testing-library/react";
import SpotlightSearch from "core/features/SpotlightSearch/SpotlightSearch";
import { MemoryRouterProvider } from "next-router-mock/MemoryRouterProvider";
import mockRouter from "next-router-mock";
import { TestApp } from "core/helpers/testutils";

describe("SpotlightSearch", () => {
  beforeEach(() => {
    jest.clearAllMocks();
    mockRouter.setCurrentUrl("/workspaces/test-workspace");
  });

  it("should type a query, filter workspaces, switch tabs, and click links", async () => {
    render(
      <MemoryRouterProvider>
        <TestApp mocks={mocks}>
          <SpotlightSearch isMac={false} isSidebarOpen={false} />
        </TestApp>
      </MemoryRouterProvider>,
    );

    fireEvent.keyDown(document, {
      key: "k",
      code: "KeyK",
      ctrlKey: true,
    });
    await waitFor(() =>
      expect(screen.getByTestId("search-input")).toBeInTheDocument(),
    );
    const searchInput = screen.getByTestId("search-input");
    fireEvent.change(searchInput, { target: { value: "test query" } });
    expect(searchInput).toHaveValue("test query");

    await waitFor(() => {
      expect(screen.getByText("Filter by Workspace")).toBeInTheDocument();
    });

    fireEvent.click(screen.getByText("Test Workspace")); // The mock data has a workspace called "Test Workspace" and expecting only one workspace in the query

    const tabs = screen.getAllByRole("tab");
    expect(tabs).toHaveLength(6);
    fireEvent.click(tabs[2]); // Switch to the tables tab
    expect(tabs[2]).toHaveAttribute("aria-selected", "true");

    await waitFor(
      () => expect(screen.getByText("Test Table")).toBeInTheDocument(),
      { timeout: 1000 }, // Account for a debounced time of 500ms in the input bar
    );
    fireEvent.keyDown(document, { key: "Enter", code: "Enter" }); // Focus and keyboard shortcuts should work
    expect(mockRouter.asPath).toBe(
      "/workspaces/test-workspace/databases/Test%20Table",
    );

    fireEvent.keyDown(document, { key: "Escape", code: "Escape" });
    await waitFor(() =>
      expect(screen.queryByTestId("search-input")).not.toBeInTheDocument(),
    );
  });
});

import {
  GetWorkspacesDocument,
  SearchDatabaseTablesDocument,
  SearchDatasetsDocument,
  SearchFilesDocument,
  SearchPipelinesDocument,
  SearchPipelineTemplatesDocument,
} from "./SpotlightSearch.generated";

const mocks = [
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
        workspaceSlugs: ["test-workspace2"],
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
        workspaceSlugs: ["test-workspace2"],
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
        workspaceSlugs: ["test-workspace2"],
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
        workspaceSlugs: ["test-workspace2"],
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
        workspaceSlugs: ["test-workspace2"],
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

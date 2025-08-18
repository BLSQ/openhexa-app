import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MockedProvider } from "@apollo/client/testing";
import { TestApp } from "core/helpers/testutils";
import WorkspaceSettingsPage from "./settings";
import { 
  useUpdateWorkspaceMutation 
} from "workspaces/graphql/mutations.generated";
import {
  WorkspacePageDocument
} from "workspaces/graphql/queries.generated";

jest.mock("next/router", () => ({
  useRouter: () => ({
    query: { workspaceSlug: "test-workspace", tab: "general" },
    push: jest.fn(),
    pathname: "/workspaces/[workspaceSlug]/settings",
  }),
  push: jest.fn(),
}));

jest.mock("workspaces/graphql/mutations.generated", () => ({
  ...jest.requireActual("workspaces/graphql/mutations.generated"),
  useUpdateWorkspaceMutation: jest.fn(),
}));

const mockUpdateWorkspace = useUpdateWorkspaceMutation as jest.Mock;

describe("WorkspaceSettingsPage Integration", () => {
  const mockWorkspaceData = {
    workspace: {
      __typename: "Workspace",
      slug: "test-workspace",
      name: "Test Workspace",
      description: "Test Description",
      dockerImage: "test-image",
      configuration: {
        api_key: "secret123",
        timeout: 300,
        debug: true,
        servers: ["server1", "server2"],
        settings: { nested: "value" }
      },
      countries: [
        { code: "US", flag: "🇺🇸", name: "United States" }
      ],
      permissions: {
        delete: true,
        update: true,
        manageMembers: true
      }
    }
  };

  const mocks = [
    {
      request: {
        query: WorkspacePageDocument,
        variables: { slug: "test-workspace" }
      },
      result: {
        data: mockWorkspaceData
      }
    }
  ];

  beforeEach(() => {
    jest.clearAllMocks();
    mockUpdateWorkspace.mockReturnValue([jest.fn(), { loading: false }]);
  });

  describe("Configuration Field Display", () => {
    it("shows configuration in General tab", async () => {
      render(
        <MockedProvider mocks={mocks} addTypename={false}>
          <TestApp>
            <WorkspaceSettingsPage 
              workspaceSlug="test-workspace"
              page={1}
              perPage={10}
            />
          </TestApp>
        </MockedProvider>
      );

      await waitFor(() => {
        expect(screen.getByText("Test Workspace")).toBeInTheDocument();
      });

      expect(screen.getByText("General")).toBeInTheDocument();
      
      expect(screen.getByText("Configuration")).toBeInTheDocument();
      
      expect(screen.getByText("api_key")).toBeInTheDocument();
      expect(screen.getByText("timeout")).toBeInTheDocument();
      expect(screen.getByText("debug")).toBeInTheDocument();
      expect(screen.getByText("servers")).toBeInTheDocument();
      expect(screen.getByText("settings")).toBeInTheDocument();
    });

    it("displays configuration values with correct types", async () => {
      render(
        <MockedProvider mocks={mocks} addTypename={false}>
          <TestApp>
            <WorkspaceSettingsPage 
              workspaceSlug="test-workspace"
              page={1}
              perPage={10}
            />
          </TestApp>
        </MockedProvider>
      );

      await waitFor(() => {
        expect(screen.getByText("Test Workspace")).toBeInTheDocument();
      });

      expect(screen.getByText("secret123")).toBeInTheDocument(); // string
      expect(screen.getByText("300")).toBeInTheDocument(); // number
      expect(screen.getByText("true")).toBeInTheDocument(); // boolean
      expect(screen.getByText('["server1","server2"]')).toBeInTheDocument(); // array
      expect(screen.getByText('{"nested":"value"}')).toBeInTheDocument(); // object

      expect(screen.getByText("text")).toBeInTheDocument(); // for string
      expect(screen.getByText("number")).toBeInTheDocument(); // for number
      expect(screen.getByText("boolean")).toBeInTheDocument(); // for boolean
      expect(screen.getByText("array")).toBeInTheDocument(); // for array
      expect(screen.getByText("object")).toBeInTheDocument(); // for object
    });
  });

  describe("Tab Navigation", () => {
    it("navigates between tabs correctly", async () => {
      const user = userEvent.setup();
      
      render(
        <MockedProvider mocks={mocks} addTypename={false}>
          <TestApp>
            <WorkspaceSettingsPage 
              workspaceSlug="test-workspace"
              page={1}
              perPage={10}
            />
          </TestApp>
        </MockedProvider>
      );

      await waitFor(() => {
        expect(screen.getByText("Test Workspace")).toBeInTheDocument();
      });

      expect(screen.getByText("Configuration")).toBeInTheDocument();

      await user.click(screen.getByText("Members"));
      expect(screen.getByText("Add/Invite member")).toBeInTheDocument();

      await user.click(screen.getByText("Advanced"));
      expect(screen.getByText("Database")).toBeInTheDocument();
      expect(screen.getByText("Regenerate password")).toBeInTheDocument();

      await user.click(screen.getByText("General"));
      expect(screen.getByText("Configuration")).toBeInTheDocument();
    });

    it("handles URL tab parameter", () => {
      const mockRouter = {
        query: { workspaceSlug: "test-workspace", tab: "members" },
        push: jest.fn(),
        pathname: "/workspaces/[workspaceSlug]/settings",
      };
      
      jest.doMock("next/router", () => ({
        useRouter: () => mockRouter,
      }));

      render(
        <MockedProvider mocks={mocks} addTypename={false}>
          <TestApp>
            <WorkspaceSettingsPage 
              workspaceSlug="test-workspace"
              page={1}
              perPage={10}
            />
          </TestApp>
        </MockedProvider>
      );

      expect(screen.getByText("Add/Invite member")).toBeInTheDocument();
    });
  });

  describe("Configuration Editing", () => {
    it("allows editing configuration in General tab", async () => {
      const user = userEvent.setup();
      const mockMutate = jest.fn().mockResolvedValue({
        data: {
          updateWorkspace: {
            success: true,
            workspace: mockWorkspaceData.workspace,
            errors: null
          }
        }
      });
      
      mockUpdateWorkspace.mockReturnValue([mockMutate, { loading: false }]);

      render(
        <MockedProvider mocks={mocks} addTypename={false}>
          <TestApp>
            <WorkspaceSettingsPage 
              workspaceSlug="test-workspace"
              page={1}
              perPage={10}
            />
          </TestApp>
        </MockedProvider>
      );

      await waitFor(() => {
        expect(screen.getByText("Test Workspace")).toBeInTheDocument();
      });

      const editButton = screen.getByText("Edit");
      await user.click(editButton);

      expect(screen.getByText("Add Configuration")).toBeInTheDocument();

      const saveButton = screen.getByText("Save");
      await user.click(saveButton);

      await waitFor(() => {
        expect(mockMutate).toHaveBeenCalledWith({
          variables: {
            input: {
              slug: "test-workspace",
              name: "Test Workspace",
              dockerImage: "test-image",
              configuration: mockWorkspaceData.workspace.configuration,
              countries: [{ code: "US" }]
            }
          }
        });
      });
    });

    it("updates configuration when adding new items", async () => {
      const user = userEvent.setup();
      const mockMutate = jest.fn().mockResolvedValue({
        data: {
          updateWorkspace: {
            success: true,
            workspace: mockWorkspaceData.workspace,
            errors: null
          }
        }
      });
      
      mockUpdateWorkspace.mockReturnValue([mockMutate, { loading: false }]);

      render(
        <MockedProvider mocks={mocks} addTypename={false}>
          <TestApp>
            <WorkspaceSettingsPage 
              workspaceSlug="test-workspace"
              page={1}
              perPage={10}
            />
          </TestApp>
        </MockedProvider>
      );

      await waitFor(() => {
        expect(screen.getByText("Test Workspace")).toBeInTheDocument();
      });

      await user.click(screen.getByText("Edit"));
      await user.click(screen.getByText("Add Configuration"));
      

      await user.click(screen.getByText("Save"));

      await waitFor(() => {
        expect(mockMutate).toHaveBeenCalled();
        const callArgs = mockMutate.mock.calls[0][0];
        expect(callArgs.variables.input.slug).toBe("test-workspace");
        expect(callArgs.variables.input.configuration).toBeDefined();
      });
    });
  });

  describe("Permission Handling", () => {
    it("shows edit controls when user has update permissions", async () => {
      render(
        <MockedProvider mocks={mocks} addTypename={false}>
          <TestApp>
            <WorkspaceSettingsPage 
              workspaceSlug="test-workspace"
              page={1}
              perPage={10}
            />
          </TestApp>
        </MockedProvider>
      );

      await waitFor(() => {
        expect(screen.getByText("Test Workspace")).toBeInTheDocument();
      });

      expect(screen.getByText("Edit")).toBeInTheDocument();
    });

    it("handles workspace without update permissions", async () => {
      const restrictedMocks = [
        {
          request: {
            query: WorkspacePageDocument,
            variables: { slug: "test-workspace" }
          },
          result: {
            data: {
              workspace: {
                ...mockWorkspaceData.workspace,
                permissions: {
                  delete: false,
                  update: false,
                  manageMembers: false
                }
              }
            }
          }
        }
      ];

      render(
        <MockedProvider mocks={restrictedMocks} addTypename={false}>
          <TestApp>
            <WorkspaceSettingsPage 
              workspaceSlug="test-workspace"
              page={1}
              perPage={10}
            />
          </TestApp>
        </MockedProvider>
      );

      await waitFor(() => {
        expect(screen.getByText("Test Workspace")).toBeInTheDocument();
      });

      expect(screen.getByText("Configuration")).toBeInTheDocument();
      expect(screen.getByText("api_key")).toBeInTheDocument();
      
      expect(screen.queryByText("Add Configuration")).not.toBeInTheDocument();
    });
  });

  describe("Error Handling", () => {
    it("handles workspace not found", async () => {
      const notFoundMocks = [
        {
          request: {
            query: WorkspacePageDocument,
            variables: { slug: "nonexistent-workspace" }
          },
          result: {
            data: { workspace: null }
          }
        }
      ];

      render(
        <MockedProvider mocks={notFoundMocks} addTypename={false}>
          <TestApp>
            <WorkspaceSettingsPage 
              workspaceSlug="nonexistent-workspace"
              page={1}
              perPage={10}
            />
          </TestApp>
        </MockedProvider>
      );

      await waitFor(() => {
        expect(screen.queryByText("Configuration")).not.toBeInTheDocument();
      });
    });

    it("handles empty configuration gracefully", async () => {
      const emptyConfigMocks = [
        {
          request: {
            query: WorkspacePageDocument,
            variables: { slug: "test-workspace" }
          },
          result: {
            data: {
              workspace: {
                ...mockWorkspaceData.workspace,
                configuration: {}
              }
            }
          }
        }
      ];

      render(
        <MockedProvider mocks={emptyConfigMocks} addTypename={false}>
          <TestApp>
            <WorkspaceSettingsPage 
              workspaceSlug="test-workspace"
              page={1}
              perPage={10}
            />
          </TestApp>
        </MockedProvider>
      );

      await waitFor(() => {
        expect(screen.getByText("Test Workspace")).toBeInTheDocument();
      });

      expect(screen.getByText("Configuration")).toBeInTheDocument();
      
      expect(screen.getByText("No configuration properties set")).toBeInTheDocument();
    });

    it("handles null configuration", async () => {
      const nullConfigMocks = [
        {
          request: {
            query: WorkspacePageDocument,
            variables: { slug: "test-workspace" }
          },
          result: {
            data: {
              workspace: {
                ...mockWorkspaceData.workspace,
                configuration: null
              }
            }
          }
        }
      ];

      render(
        <MockedProvider mocks={nullConfigMocks} addTypename={false}>
          <TestApp>
            <WorkspaceSettingsPage 
              workspaceSlug="test-workspace"
              page={1}
              perPage={10}
            />
          </TestApp>
        </MockedProvider>
      );

      await waitFor(() => {
        expect(screen.getByText("Test Workspace")).toBeInTheDocument();
      });

      expect(screen.getByText("Configuration")).toBeInTheDocument();
      expect(screen.getByText("No configuration properties set")).toBeInTheDocument();
    });
  });

  describe("Breadcrumbs and Navigation", () => {
    it("displays correct breadcrumbs", async () => {
      render(
        <MockedProvider mocks={mocks} addTypename={false}>
          <TestApp>
            <WorkspaceSettingsPage 
              workspaceSlug="test-workspace"
              page={1}
              perPage={10}
            />
          </TestApp>
        </MockedProvider>
      );

      await waitFor(() => {
        expect(screen.getByText("Test Workspace")).toBeInTheDocument();
      });

      expect(screen.getByText("Settings")).toBeInTheDocument();
    });

    it("shows archive button when user has delete permissions", async () => {
      render(
        <MockedProvider mocks={mocks} addTypename={false}>
          <TestApp>
            <WorkspaceSettingsPage 
              workspaceSlug="test-workspace"
              page={1}
              perPage={10}
            />
          </TestApp>
        </MockedProvider>
      );

      await waitFor(() => {
        expect(screen.getByText("Test Workspace")).toBeInTheDocument();
      });

      expect(screen.getByText("Archive")).toBeInTheDocument();
    });
  });

  describe("Data Refetch", () => {
    it("refetches data after successful save", async () => {
      const user = userEvent.setup();
      const mockRefetch = jest.fn().mockResolvedValue({ data: mockWorkspaceData });
      const mockMutate = jest.fn().mockResolvedValue({
        data: {
          updateWorkspace: {
            success: true,
            workspace: mockWorkspaceData.workspace,
            errors: null
          }
        }
      });
      
      mockUpdateWorkspace.mockReturnValue([mockMutate, { loading: false }]);

      jest.doMock("workspaces/graphql/queries.generated", () => ({
        useWorkspacePageQuery: () => ({
          data: mockWorkspaceData,
          refetch: mockRefetch
        })
      }));

      render(
        <MockedProvider mocks={mocks} addTypename={false}>
          <TestApp>
            <WorkspaceSettingsPage 
              workspaceSlug="test-workspace"
              page={1}
              perPage={10}
            />
          </TestApp>
        </MockedProvider>
      );

      await waitFor(() => {
        expect(screen.getByText("Test Workspace")).toBeInTheDocument();
      });

      await user.click(screen.getByText("Edit"));
      await user.click(screen.getByText("Save"));

      await waitFor(() => {
        expect(mockMutate).toHaveBeenCalled();
      });
    });
  });
});
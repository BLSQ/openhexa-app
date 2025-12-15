import React from "react";
import {
  fireEvent,
  render,
  screen,
  waitFor,
  within,
} from "@testing-library/react";
import WorkspaceWebappPage from "pages/workspaces/[workspaceSlug]/webapps/[webappSlug]";
import { toast } from "react-toastify";
import { TestApp } from "core/helpers/testutils";
import {
  WorkspacePageDocument,
  WorkspaceWebappPageDocument,
} from "workspaces/graphql/queries.generated";
import { SidebarMenuDocument } from "workspaces/features/SidebarMenu/SidebarMenu.generated";
import { MockedResponse } from "@apollo/client/testing";
import { DeleteWebappDocument } from "workspaces/graphql/mutations.generated";
import { UpdateWebappDocument } from "webapps/graphql/mutations.generated";

jest.mock("react-toastify", () => ({
  toast: {
    success: jest.fn(),
    error: jest.fn(),
  },
}));

jest.mock("next-i18next", () => ({
  useTranslation: jest.fn().mockReturnValue({ t: (key: string) => key }),
}));

const graphqlMocks: MockedResponse[] = [
  {
    request: {
      query: SidebarMenuDocument,
      variables: {
        page: 1,
        perPage: 2000,
      },
    },
    maxUsageCount: Infinity,
    result: {
      data: {
        pendingWorkspaceInvitations: { totalItems: 1 },
        workspaces: {
          totalItems: 2,
          items: [
            {
              slug: "workspace-1",
              name: "Workspace 1",
              countries: [{ code: "US", flag: "🇺🇸" }],
            },
            {
              slug: "workspace-2",
              name: "Workspace 2",
              countries: [{ code: "FR", flag: "🇫🇷" }],
            },
          ],
        },
      },
    },
  },
  {
    request: {
      query: WorkspaceWebappPageDocument,
      variables: {
        workspaceSlug: "test-workspace",
        webappSlug: "test-webapp",
      },
    },
    result: {
      data: {
        webapp: {
          __typename: "Webapp",
          id: "1",
          slug: "test-webapp",
          name: "Test Webapp",
          description: "Test Webapp Description",
          url: "https://test-url.com",
          type: "IFRAME",
          isFavorite: false,
          icon: "",
          createdBy: {
            displayName: "User 1",
            avatar: {
              initials: "U",
              color: "",
            },
          },
          permissions: {
            delete: true,
            update: true,
          },
        },
        workspace: {
          __typename: "Workspace",
          slug: "test-workspace",
          name: "Test Workspace",
          countries: [],
          shortcuts: [],
          organization: null,
          permissions: {
            launchNotebookServer: false,
            manageMembers: false,
            update: true,
          },
        },
      },
    },
  },
  {
    request: {
      query: WorkspacePageDocument,
      variables: {
        slug: "test-workspace",
      },
    },
    result: {
      data: {
        workspace: {
          slug: "test-workspace",
          name: "Test Workspace",
          countries: [],
          shortcuts: [],
          organization: null,
          permissions: {
            launchNotebookServer: false,
            manageMembers: false,
            update: true,
          },
        },
      },
    },
  },
];

describe("WorkspaceWebappPage", () => {
  it("can update a web app", async () => {
    render(
      <TestApp
        mocks={graphqlMocks.concat([
          {
            request: {
              query: UpdateWebappDocument,
              variables: {
                input: {
                  id: "1",
                  name: "Updated Webapp",
                  icon: "",
                  content: {
                    iframe: {
                      url: "https://updated-url.com",
                    },
                  },
                },
              },
            },
            result: {
              data: {
                updateWebapp: {
                  success: true,
                  errors: [],
                },
              },
            },
          },
          {
            request: {
              query: SidebarMenuDocument,
              variables: {
                page: 1,
                perPage: 2000,
              },
            },
            result: {
              data: {
                pendingWorkspaceInvitations: { totalItems: 1 },
                workspaces: {
                  totalItems: 2,
                  items: [
                    {
                      slug: "workspace-1",
                      name: "Workspace 1",
                      countries: [{ code: "US", flag: "🇺🇸" }],
                    },
                    {
                      slug: "workspace-2",
                      name: "Workspace 2",
                      countries: [{ code: "FR", flag: "🇫🇷" }],
                    },
                  ],
                },
              },
            },
          },
          {
            request: {
              query: WorkspaceWebappPageDocument,
              variables: {
                workspaceSlug: "test-workspace",
                webappSlug: "test-webapp",
              },
            },
            result: {
              data: {
                webapp: {
                  __typename: "Webapp",
                  id: "1",
                  slug: "test-webapp",
                  name: "Updated Webapp",
                  description: "Test Webapp Description",
                  url: "https://updated-url.com",
                  type: "IFRAME",
                  isFavorite: false,
                  icon: "",
                  createdBy: {
                    displayName: "User 1",
                    avatar: {
                      initials: "U",
                      color: "",
                    },
                  },
                  permissions: {
                    delete: true,
                    update: true,
                  },
                },
                workspace: {
                  __typename: "Workspace",
                  slug: "test-workspace",
                  name: "Test Workspace",
                  countries: [],
                  shortcuts: [],
                  organization: null,
                  permissions: {
                    launchNotebookServer: false,
                    manageMembers: false,
                    update: true,
                  },
                },
              },
            },
          },
          {
            request: {
              query: SidebarMenuDocument,
              variables: {
                page: 1,
                perPage: 2000,
              },
            },
            result: {
              data: {
                pendingWorkspaceInvitations: { totalItems: 1 },
                workspaces: {
                  totalItems: 2,
                  items: [
                    {
                      slug: "workspace-1",
                      name: "Workspace 1",
                      countries: [{ code: "US", flag: "🇺🇸" }],
                    },
                    {
                      slug: "workspace-2",
                      name: "Workspace 2",
                      countries: [{ code: "FR", flag: "🇫🇷" }],
                    },
                  ],
                },
              },
            },
          },
          {
            request: {
              query: WorkspaceWebappPageDocument,
              variables: {
                workspaceSlug: "test-workspace",
                webappSlug: "test-webapp",
              },
            },
            result: {
              data: {
                webapp: {
                  __typename: "Webapp",
                  id: "1",
                  slug: "test-webapp",
                  name: "Updated Webapp",
                  description: "Test Webapp Description",
                  url: "https://updated-url.com",
                  type: "IFRAME",
                  isFavorite: false,
                  icon: "",
                  createdBy: {
                    displayName: "User 1",
                    avatar: {
                      initials: "U",
                      color: "",
                    },
                  },
                  permissions: {
                    delete: true,
                    update: true,
                  },
                },
                workspace: {
                  __typename: "Workspace",
                  slug: "test-workspace",
                  name: "Test Workspace",
                  countries: [],
                  shortcuts: [],
                  organization: null,
                  permissions: {
                    launchNotebookServer: false,
                    manageMembers: false,
                    update: true,
                  },
                },
              },
            },
          },
        ])}
      >
        <WorkspaceWebappPage
          webappSlug="test-webapp"
          workspaceSlug="test-workspace"
        />
      </TestApp>,
    );

    await waitFor(() => {
      expect(screen.getByText("Webapp Details")).toBeInTheDocument();
    });

    fireEvent.click(screen.getByRole("button", { name: "Edit" }));

    const nameParent = screen
      .getByText("Name")
      .closest("div") as HTMLDivElement;
    const nameInput = within(nameParent).getByRole("textbox");
    fireEvent.change(nameInput, { target: { value: "Updated Webapp" } });

    const urlParent = screen.getByText("URL").closest("div") as HTMLDivElement;
    const urlInput = within(urlParent).getByRole("textbox");
    fireEvent.change(urlInput, {
      target: { value: "https://updated-url.com" },
    });

    fireEvent.click(screen.getByRole("button", { name: "Save" }));

    await waitFor(() => {
      expect(toast.success).toHaveBeenCalledWith("Webapp updated successfully");
    });
  });

  it("can delete a web app", async () => {
    render(
      <TestApp
        mocks={graphqlMocks.concat({
          request: {
            query: DeleteWebappDocument,
            variables: {
              input: {
                id: "1",
              },
            },
          },
          result: {
            data: {
              deleteWebapp: {
                success: true,
              },
            },
          },
        })}
      >
        <WorkspaceWebappPage
          webappSlug="test-webapp"
          workspaceSlug="test-workspace"
        />
      </TestApp>,
    );

    await waitFor(() => {
      expect(screen.getByText("Webapp Details")).toBeInTheDocument();
    });

    fireEvent.click(screen.getByRole("button", { name: "Delete" }));

    await waitFor(() => {
      expect(screen.getByText("Delete webapp")).toBeInTheDocument();
    });

    fireEvent.click(screen.getByRole("button", { name: "Delete" }));

    await waitFor(() => {
      expect(toast.success).toHaveBeenCalledWith(
        "Webapp deleted successfully.",
      );
    });
  });
});

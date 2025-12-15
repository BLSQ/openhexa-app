import React from "react";
import {
  fireEvent,
  render,
  screen,
  waitFor,
  within,
} from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import WebappCreatePage from "pages/workspaces/[workspaceSlug]/webapps/create";
import { toast } from "react-toastify";
import { TestApp } from "core/helpers/testutils";
import { SidebarMenuDocument } from "workspaces/features/SidebarMenu/SidebarMenu.generated";
import { CreateWebappDocument } from "webapps/graphql/mutations.generated";
import { MockedResponse } from "@apollo/client/testing";
import mockRouter from "next-router-mock";

jest.mock("react-toastify", () => ({
  toast: {
    success: jest.fn(),
    error: jest.fn(),
  },
}));

jest.mock("next-i18next", () => ({
  useTranslation: jest.fn().mockReturnValue({ t: (key: string) => key }),
}));

jest.mock("next/router", () => require("next-router-mock"));

const mockWorkspace = {
  slug: "test-workspace",
  countries: [],
  shortcuts: [],
  permissions: {
    launchNotebookServer: false,
    manageMembers: false,
  },
};

const graphqlMocks: MockedResponse[] = [
  {
    request: {
      query: SidebarMenuDocument,
      variables: {
        page: 1,
        perPage: 5,
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
      query: CreateWebappDocument,
      variables: {
        input: {
          workspaceSlug: "test-workspace",
          name: "Test Webapp",
          content: {
            iframe: {
              url: "http://test-webapp.com",
            },
          },
        },
      },
    },
    result: {
      data: {
        createWebapp: {
          success: true,
          errors: [],
          webapp: {
            id: "1",
          },
        },
      },
    },
  },
];

describe("WebappCreatePage", () => {
  beforeEach(() => {
    jest.clearAllMocks();
    mockRouter.setCurrentUrl("/workspaces/test-workspace/webapps/create");
  });

  it("can create a web app", async () => {
    render(
      <TestApp mocks={graphqlMocks}>
        <WebappCreatePage workspace={mockWorkspace} />
      </TestApp>,
    );

    await waitFor(() => {
      expect(screen.getByText("New Webapp")).toBeInTheDocument();
    });

    const nameParent = screen
      .getByText("Name")
      .closest("div") as HTMLDivElement;
    const nameInput = within(nameParent).getByRole("textbox");
    const urlParent = screen.getByText("URL").closest("div") as HTMLDivElement;
    const urlInput = within(urlParent).getByRole("textbox");

    fireEvent.change(nameInput, { target: { value: "Test Webapp" } });
    fireEvent.change(urlInput, {
      target: { value: "http://test-webapp.com" },
    });

    const typeParent = screen.getByText("Type").closest("div") as HTMLDivElement;
    const typeCombobox = within(typeParent).getByRole("combobox");
    await userEvent.click(typeCombobox);

    await waitFor(() => {
      expect(screen.getByRole("option", { name: "iFrame" })).toBeInTheDocument();
    });

    await userEvent.click(screen.getByRole("option", { name: "iFrame" }));

    const createButton = screen.getByRole("button", { name: "Create" });
    fireEvent.click(createButton);

    await waitFor(() => {
      expect(toast.success).toHaveBeenCalledWith("Webapp created successfully");
    });

    expect(mockRouter.asPath).toBe("/workspaces/test-workspace/webapps");
  });

  it("handles null webapp response", async () => {
    const nullWebappMock: MockedResponse[] = [
      {
        request: {
          query: SidebarMenuDocument,
          variables: {
            page: 1,
            perPage: 5,
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
          query: CreateWebappDocument,
          variables: {
            input: {
              workspaceSlug: "test-workspace",
              name: "Test Webapp",
              content: {
                iframe: {
                  url: "http://test-webapp.com",
                },
              },
            },
          },
        },
        result: {
          data: {
            createWebapp: {
              success: true,
              errors: [],
              webapp: null,
            },
          },
        },
      },
    ];

    render(
      <TestApp mocks={nullWebappMock}>
        <WebappCreatePage workspace={mockWorkspace} />
      </TestApp>,
    );

    await waitFor(() => {
      expect(screen.getByText("New Webapp")).toBeInTheDocument();
    });

    const nameParent = screen
      .getByText("Name")
      .closest("div") as HTMLDivElement;
    const nameInput = within(nameParent).getByRole("textbox");
    const urlParent = screen.getByText("URL").closest("div") as HTMLDivElement;
    const urlInput = within(urlParent).getByRole("textbox");

    fireEvent.change(nameInput, { target: { value: "Test Webapp" } });
    fireEvent.change(urlInput, {
      target: { value: "http://test-webapp.com" },
    });

    const typeParent = screen.getByText("Type").closest("div") as HTMLDivElement;
    const typeCombobox = within(typeParent).getByRole("combobox");
    await userEvent.click(typeCombobox);

    await waitFor(() => {
      expect(screen.getByRole("option", { name: "iFrame" })).toBeInTheDocument();
    });

    await userEvent.click(screen.getByRole("option", { name: "iFrame" }));

    const createButton = screen.getByRole("button", { name: "Create" });
    fireEvent.click(createButton);

    await waitFor(() => {
      expect(toast.error).toHaveBeenCalledWith(
        "An error occurred while creating the webapp",
      );
    });

    expect(mockRouter.asPath).toBe("/workspaces/test-workspace/webapps/create");
  });

  it("handles network errors", async () => {
    const errorMock: MockedResponse[] = [
      {
        request: {
          query: SidebarMenuDocument,
          variables: {
            page: 1,
            perPage: 5,
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
          query: CreateWebappDocument,
          variables: {
            input: {
              workspaceSlug: "test-workspace",
              name: "Test Webapp",
              content: {
                iframe: {
                  url: "http://test-webapp.com",
                },
              },
            },
          },
        },
        error: new Error("Network error"),
      },
    ];

    render(
      <TestApp mocks={errorMock}>
        <WebappCreatePage workspace={mockWorkspace} />
      </TestApp>,
    );

    await waitFor(() => {
      expect(screen.getByText("New Webapp")).toBeInTheDocument();
    });

    const nameParent = screen
      .getByText("Name")
      .closest("div") as HTMLDivElement;
    const nameInput = within(nameParent).getByRole("textbox");
    const urlParent = screen.getByText("URL").closest("div") as HTMLDivElement;
    const urlInput = within(urlParent).getByRole("textbox");

    fireEvent.change(nameInput, { target: { value: "Test Webapp" } });
    fireEvent.change(urlInput, {
      target: { value: "http://test-webapp.com" },
    });

    const typeParent = screen.getByText("Type").closest("div") as HTMLDivElement;
    const typeCombobox = within(typeParent).getByRole("combobox");
    await userEvent.click(typeCombobox);

    await waitFor(() => {
      expect(screen.getByRole("option", { name: "iFrame" })).toBeInTheDocument();
    });

    await userEvent.click(screen.getByRole("option", { name: "iFrame" }));

    const createButton = screen.getByRole("button", { name: "Create" });
    fireEvent.click(createButton);

    await waitFor(() => {
      expect(toast.error).toHaveBeenCalledWith(
        "An error occurred while creating the webapp",
      );
    });

    expect(mockRouter.asPath).toBe("/workspaces/test-workspace/webapps/create");
  });
});

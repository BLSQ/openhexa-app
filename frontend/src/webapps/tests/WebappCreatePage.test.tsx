import React from "react";
import {
  fireEvent,
  render,
  screen,
  waitFor,
  within,
} from "@testing-library/react";
import WebappCreatePage from "pages/workspaces/[workspaceSlug]/webapps/create";
import { toast } from "react-toastify";
import { TestApp } from "core/helpers/testutils";
import { SidebarMenuDocument } from "workspaces/features/SidebarMenu/SidebarMenu.generated";
import { CreateWebappDocument } from "webapps/graphql/mutations.generated";
import { MockedResponse } from "@apollo/client/testing";

jest.mock("react-toastify", () => ({
  toast: {
    success: jest.fn(),
    error: jest.fn(),
  },
}));

jest.mock("next-i18next", () => ({
  useTranslation: jest.fn().mockReturnValue({ t: (key: string) => key }),
}));

const mockWorkspace = {
  slug: "test-workspace",
  countries: [],
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
          url: "http://test-webapp.com",
        },
      },
    },
    result: {
      data: {
        createWebapp: {
          webapp: {
            id: "1",
            name: "Test Webapp",
          },
        },
      },
    },
  },
];

describe("WebappCreatePage", () => {
  it("can create a web app", async () => {
    render(
      <TestApp mocks={graphqlMocks} me={{ features: [{ code: "webapps" }] }}>
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
    fireEvent.change(screen.getByLabelText("Change Icon"), {
      target: { files: [new File([""], "icon.png", { type: "image/png" })] },
    });

    fireEvent.click(screen.getByRole("button", { name: "Create" }));

    await waitFor(() => {
      expect(toast.success).toHaveBeenCalledWith("Webapp created successfully");
    });
  });
});

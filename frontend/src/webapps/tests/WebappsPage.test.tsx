import React from "react";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import WebappsPage from "pages/workspaces/[workspaceSlug]/webapps";
import { toast } from "react-toastify";
import { TestApp } from "core/helpers/testutils";
import { SidebarMenuDocument } from "workspaces/features/SidebarMenu/SidebarMenu.generated";
import { MockedResponse } from "@apollo/client/testing";
import { WorkspaceWebappsPageDocument } from "workspaces/graphql/queries.generated";
import {
  AddToFavoritesDocument,
  RemoveFromFavoritesDocument,
} from "../graphql/mutations.generated";

jest.mock("react-toastify", () => ({
  toast: {
    success: jest.fn(),
    error: jest.fn(),
  },
}));

jest.mock("next-i18next", () => ({
  useTranslation: jest.fn().mockReturnValue({ t: (key: string) => key }),
  i18n: { t: (key: string) => key },
}));

const mockWorkspace = {
  __typename: "Workspace",
  slug: "test-workspace",
  name: "Test Workspace",
  countries: [],
  shortcuts: [],
  organization: {
    id: "org1",
    name: "Test Organization",
    shortName: "Test Organization",
    permissions: {
      createWorkspace: true,
    },
  },
  permissions: {
    launchNotebookServer: false,
    manageMembers: false,
    update: true,
  },
};

const webapp = (id: string) => ({
  __typename: "Webapp",
  id: id,
  name: `Webapp ${id}`,
  isFavorite: id === "2",
  isShortcut: false,
  description: "Webapp description",
  url: `https://example${id}.com`,
  icon: "",
  createdBy: {
    __typename: "User",
    id: id,
    displayName: `User ${id}`,
    firstName: `FirstName ${id}`,
    lastName: `LastName ${id}`,
    email: `email${id}@email.com`,
    avatar: {
      initials: "U",
      color: "",
    },
  },
  permissions: {
    update: true,
    delete: true,
  },
  workspace: mockWorkspace,
});

const sidebarMenuMock: MockedResponse = {
  request: {
    query: SidebarMenuDocument,
    variables: {
      page: 1,
      perPage: 2000,
      organizationId: mockWorkspace.organization.id,
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
};

const graphqlMocks: MockedResponse[] = [
  sidebarMenuMock,
  {
    request: {
      query: WorkspaceWebappsPageDocument,
      variables: {
        workspaceSlug: "test-workspace",
        page: 1,
        perPage: 15,
      },
    },
    result: {
      data: {
        workspace: mockWorkspace,
        webapps: {
          pageNumber: 1,
          totalPages: 2,
          totalItems: 16,
          items: Array.from({ length: 15 }, (_, index) =>
            webapp((index + 1).toString()),
          ),
        },
        favoriteWebapps: {
          items: [],
          totalPages: 0,
          totalItems: 0,
        },
      },
    },
  },
];

describe("WebappsPage", () => {
  it("renders the list of webapps", async () => {
    render(
      <TestApp mocks={graphqlMocks}>
        <WebappsPage workspaceSlug="test-workspace" page={1} perPage={15} />
      </TestApp>,
    );

    await waitFor(() => {
      expect(screen.getByText("Webapp 1")).toBeInTheDocument();
    });
  });

  it("adds a webapp to favorites", async () => {
    render(
      <TestApp
        mocks={graphqlMocks.concat({
          request: {
            query: AddToFavoritesDocument,
            variables: { input: { webappId: "1" } },
          },
          result: {
            data: {
              addToFavorites: {
                success: true,
              },
            },
          },
        })}
      >
        <WebappsPage workspaceSlug="test-workspace" page={1} perPage={15} />
      </TestApp>,
    );

    await waitFor(() => {
      expect(screen.getByText("Webapp 1")).toBeInTheDocument();
    });

    fireEvent.click(screen.getByTestId("favorite-button-1"));

    await waitFor(() => {
      expect(toast.success).toHaveBeenCalledWith("Added to favorites");
    });
  });

  it("removes a webapp from favorites", async () => {
    render(
      <TestApp
        mocks={graphqlMocks.concat({
          request: {
            query: RemoveFromFavoritesDocument,
            variables: { input: { webappId: "2" } },
          },
          result: {
            data: {
              removeFromFavorites: {
                success: true,
              },
            },
          },
        })}
      >
        <WebappsPage workspaceSlug="test-workspace" page={1} perPage={15} />
      </TestApp>,
    );

    await waitFor(() => {
      expect(screen.getByText("Webapp 2")).toBeInTheDocument();
    });

    fireEvent.click(screen.getByTestId("favorite-button-2"));

    await waitFor(() => {
      expect(toast.success).toHaveBeenCalledWith("Removed from favorites");
    });
  });

  it("handles pagination", async () => {
    render(
      <TestApp
        mocks={graphqlMocks.concat({
          request: {
            query: WorkspaceWebappsPageDocument,
            variables: {
              workspaceSlug: "test-workspace",
              page: 2,
              perPage: 15,
            },
          },
          result: {
            data: {
              workspace: mockWorkspace,
              webapps: {
                pageNumber: 2,
                totalPages: 2,
                totalItems: 16,
                items: [webapp("16")],
              },
              favoriteWebapps: {
                items: [],
                totalPages: 0,
                totalItems: 0,
              },
            },
          },
        })}
      >
        <WebappsPage workspaceSlug="test-workspace" page={1} perPage={15} />
      </TestApp>,
    );

    await waitFor(() => {
      expect(screen.getByText("Webapp 1")).toBeInTheDocument();
    });

    const previousButton = screen.getByRole("button", { name: /Previous/i });
    const nextButton = previousButton.nextElementSibling as HTMLButtonElement;

    await waitFor(() => {
      expect(nextButton).toBeInTheDocument();
    });

    fireEvent.click(nextButton);

    await waitFor(() => {
      expect(screen.getByText("Webapp 16")).toBeInTheDocument();
    });
  });
});

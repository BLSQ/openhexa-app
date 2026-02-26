import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { MockedProvider } from "@apollo/client/testing";
import OrganizationPage from "pages/organizations/[organizationId]";
import { OrganizationWorkspacesDocument } from "organizations/graphql/queries.generated";
import mockRouter from "next-router-mock";
import { TestApp } from "core/helpers/testutils";

jest.mock("next/router", () => require("next-router-mock"));
jest.mock("next-i18next", () => ({
  useTranslation: jest.fn().mockReturnValue({ t: (key: string) => key }),
}));

const organization = {
  id: "org-1",
  name: "Test Organization",
  shortName: "Test Org",
  permissions: {
    createWorkspace: { isAllowed: true, reasons: [] },
    archiveWorkspace: true,
    manageMembers: true,
    manageOwners: true,
  },
  members: {
    totalItems: 0,
  },
  workspaces: {
    totalItems: 2,
    items: [
      {
        slug: "workspace-1",
        name: "Workspace 1",
        countries: [{ code: "US" }],
      },
      {
        slug: "workspace-2",
        name: "Workspace 2",
        countries: [],
      },
    ],
  },
} as any;

const mocks = [
  {
    request: {
      query: OrganizationWorkspacesDocument,
      variables: {
        organizationId: "org-1",
        page: 1,
        perPage: 15,
        query: "",
      },
    },
    result: {
      data: {
        organization: {
          __typename: "Organization",
          id: "org-1",
          name: "Test Organization",
          shortName: "Test Org",
          permissions: {
            __typename: "OrganizationPermissions",
            createWorkspace: {
              __typename: "CreateWorkspacePermission",
              isAllowed: true,
              reasons: [],
            },
            archiveWorkspace: true,
            manageMembers: true,
            manageOwners: true,
          },
          members: {
            __typename: "OrganizationMembershipPage",
            totalItems: 0,
          },
          workspaces: {
            __typename: "WorkspacePage",
            totalItems: 2,
            items: [
              {
                __typename: "Workspace",
                slug: "workspace-1",
                name: "Workspace 1",
                countries: [{ __typename: "Country", code: "US" }],
              },
              {
                __typename: "Workspace",
                slug: "workspace-2",
                name: "Workspace 2",
                countries: [],
              },
            ],
          },
        },
        workspaces: {
          __typename: "WorkspacePage",
          totalItems: 2,
          pageNumber: 1,
          totalPages: 1,
          items: [
            {
              __typename: "Workspace",
              slug: "workspace-1",
              name: "Workspace 1",
              createdAt: new Date().toISOString(),
              updatedAt: new Date().toISOString(),
              countries: [{ __typename: "Country", code: "US" }],
              createdBy: {
                __typename: "User",
                displayName: "Tester",
                avatar: { __typename: "Avatar", initials: "T", color: "blue" },
              },
              members: {
                __typename: "WorkspaceMembershipPage",
                totalItems: 0,
              },
              permissions: {
                __typename: "WorkspacePermissions",
                manageMembers: true,
                delete: true,
              },
            },
            {
              __typename: "Workspace",
              slug: "workspace-2",
              name: "Workspace 2",
              createdAt: new Date().toISOString(),
              updatedAt: new Date().toISOString(),
              countries: [],
              createdBy: {
                __typename: "User",
                displayName: "Tester",
                avatar: { __typename: "Avatar", initials: "T", color: "blue" },
              },
              members: {
                __typename: "WorkspaceMembershipPage",
                totalItems: 0,
              },
              permissions: {
                __typename: "WorkspacePermissions",
                manageMembers: true,
                delete: true,
              },
            },
          ],
        },
      },
    },
  },
];

const emptyMocks: any[] = [];

describe("OrganizationPage", () => {
  beforeEach(() => {
    mockRouter.setCurrentUrl("/");
  });

  it("renders organization name and workspaces", async () => {
    render(
      <TestApp>
        <MockedProvider mocks={mocks}>
          <OrganizationPage organization={organization} />
        </MockedProvider>
      </TestApp>,
    );

    expect(screen.getByText("Test Organization")).toBeInTheDocument();
    expect(screen.getByText("2 workspaces")).toBeInTheDocument();
    await waitFor(() => {
      expect(screen.getByText("Workspace 1")).toBeInTheDocument();
    });
    expect(screen.getByText("Workspace 2")).toBeInTheDocument();
  });

  it("renders nothing if organization is null", () => {
    render(
      <TestApp>
        <MockedProvider mocks={emptyMocks}>
          <OrganizationPage organization={null} />
        </MockedProvider>
      </TestApp>,
    );

    expect(screen.queryByText("Test Organization")).not.toBeInTheDocument();
  });

  it("opens create workspace dialog when 'Create Workspace' button is clicked", () => {
    render(
      <TestApp>
        <MockedProvider mocks={mocks}>
          <OrganizationPage organization={organization} />
        </MockedProvider>
      </TestApp>,
    );

    const createButton = screen.getByText("Create Workspace");
    fireEvent.click(createButton);

    expect(screen.getByText("Create a workspace")).toBeInTheDocument();
  });

  it("opens archive workspace dialog when 'Archive' button is clicked", async () => {
    render(
      <TestApp>
        <MockedProvider mocks={mocks}>
          <OrganizationPage organization={organization} />
        </MockedProvider>
      </TestApp>,
    );

    await waitFor(() => {
      expect(screen.getByText("Workspace 1")).toBeInTheDocument();
    });

    const archiveButtons = screen.getAllByText("Archive");
    fireEvent.click(archiveButtons[0]);

    await waitFor(() =>
      expect(screen.getByText(/You're about to archive/)).toBeInTheDocument(),
    );
  });

  it("navigates to the settings page when 'Settings' button is clicked", async () => {
    render(
      <TestApp>
        <MockedProvider mocks={mocks}>
          <OrganizationPage organization={organization} />
        </MockedProvider>
      </TestApp>,
    );

    await waitFor(() => {
      expect(screen.getByText("Workspace 1")).toBeInTheDocument();
    });

    const settingsButton = screen.getAllByText("Settings")[0];
    fireEvent.click(settingsButton);

    await waitFor(() =>
      expect(mockRouter.asPath).toBe("/workspaces/workspace-1/settings"),
    );
  });
});

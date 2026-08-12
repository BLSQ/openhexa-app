import { MockedResponse } from "@apollo/client/testing";
import { render, screen } from "@testing-library/react";
import { TestApp } from "core/helpers/testutils";
import { AccountPageDocument } from "identity/graphql/queries.generated";
import mockRouter from "next-router-mock";
import AccountPage from "pages/user/account";

jest.mock("identity/graphql/mutations.generated", () => ({
  ...jest.requireActual("identity/graphql/mutations.generated"),
  __esModule: true,
}));

describe("AccountPage", () => {
  beforeEach(() => {
    mockRouter.setCurrentUrl("/user/account");
  });

  it("renders without two-factor enabled", async () => {
    const graphqlMocks: MockedResponse[] = [
      {
        request: {
          query: AccountPageDocument,
        },
        result: {
          data: {
            pendingWorkspaceInvitations: { totalItems: 0, items: [] },
            workspaces: { totalItems: 0, items: [] },
            me: {
              __typename: "Me",
              hasTwoFactorEnabled: false,
              user: {
                __typename: "User",
                id: "id",
                avatar: {
                  __typename: "Avatar",
                  color: "gray",
                  initials: "AB",
                },
                firstName: "Alphonsa",
                lastName: "Brown",
                dateJoined: "20230120",
                displayName: "Alphonse Brown",
                email: "abrown@bluesquarehub.com",
                language: "en",
                analyticsEnabled: false,
              },
            },
          },
        },
      },
    ];

    const { container } = render(
      <TestApp mocks={graphqlMocks}>
        <AccountPage />
      </TestApp>,
    );
    const elm = await screen.findByText("Alphonse Brown");
    expect(elm).toBeInTheDocument();

    const securitySection = screen.queryByText("Currently disabled");
    expect(securitySection).toBeInTheDocument();
  });

  it("renders with two-factor enabled and not active for the user", async () => {
    const graphqlMocks: MockedResponse[] = [
      {
        request: {
          query: AccountPageDocument,
        },
        result: {
          data: {
            pendingWorkspaceInvitations: { totalItems: 0, items: [] },
            workspaces: { totalItems: 0, items: [] },
            me: {
              __typename: "Me",
              hasTwoFactorEnabled: false,
              user: {
                __typename: "User",
                id: "id",
                avatar: {
                  __typename: "Avatar",
                  color: "gray",
                  initials: "AB",
                },
                firstName: "Alphonsa",
                lastName: "Brown",
                dateJoined: "20230120",
                displayName: "Alphonse Brown",
                email: "abrown@bluesquarehub.com",
                language: "en",
                analyticsEnabled: false,
              },
            },
          },
        },
      },
    ];

    const { container } = render(
      <TestApp mocks={graphqlMocks}>
        <AccountPage />
      </TestApp>,
    );
    const elm = await screen.findByText("Alphonse Brown");
    expect(elm).toBeInTheDocument();

    const securitySection = screen.queryByText("Security");
    expect(securitySection).toBeInTheDocument();

    const twoFactorButton = screen.queryByText("Enable", {
      selector: "button",
    });
    expect(twoFactorButton).toBeInTheDocument();
  });

  it("lists an access token per workspace, gated by the generateToken permission", async () => {
    const graphqlMocks: MockedResponse[] = [
      {
        request: {
          query: AccountPageDocument,
        },
        result: {
          data: {
            pendingWorkspaceInvitations: { totalItems: 0, items: [] },
            workspaces: {
              __typename: "WorkspacePage",
              totalItems: 2,
              items: [
                {
                  __typename: "Workspace",
                  slug: "editor-workspace",
                  name: "Editor Workspace",
                  currentMembership: {
                    __typename: "WorkspaceMembership",
                    role: "EDITOR",
                  },
                  permissions: {
                    __typename: "WorkspacePermissions",
                    generateToken: true,
                  },
                },
                {
                  __typename: "Workspace",
                  slug: "viewer-workspace",
                  name: "Viewer Workspace",
                  currentMembership: {
                    __typename: "WorkspaceMembership",
                    role: "VIEWER",
                  },
                  permissions: {
                    __typename: "WorkspacePermissions",
                    generateToken: false,
                  },
                },
              ],
            },
            me: {
              __typename: "Me",
              hasTwoFactorEnabled: false,
              user: {
                __typename: "User",
                id: "id",
                avatar: {
                  __typename: "Avatar",
                  color: "gray",
                  initials: "AB",
                },
                firstName: "Alphonsa",
                lastName: "Brown",
                dateJoined: "20230120",
                displayName: "Alphonse Brown",
                email: "abrown@bluesquarehub.com",
                language: "en",
                analyticsEnabled: false,
              },
            },
          },
        },
      },
    ];

    render(
      <TestApp mocks={graphqlMocks}>
        <AccountPage />
      </TestApp>,
    );

    expect(await screen.findByText("Access tokens")).toBeInTheDocument();
    expect(screen.getByText("Editor Workspace")).toBeInTheDocument();
    expect(screen.getByText("Viewer Workspace")).toBeInTheDocument();

    // Only the workspace the user can generate a token for offers a Show button
    expect(screen.getAllByRole("button", { name: "Show" })).toHaveLength(1);
    expect(screen.getByText("Not available for viewers")).toBeInTheDocument();
  });
});

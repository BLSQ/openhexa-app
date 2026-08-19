import { MockedResponse } from "@apollo/client/testing";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { TestApp } from "core/helpers/testutils";
import {
  AccountAccessTokensDocument,
  AccountPageDocument,
} from "identity/graphql/queries.generated";
import mockRouter from "next-router-mock";
import AccountPage from "pages/user/account";

jest.mock("identity/graphql/mutations.generated", () => ({
  ...jest.requireActual("identity/graphql/mutations.generated"),
  __esModule: true,
}));

const accountPageMock = (): MockedResponse => ({
  request: {
    query: AccountPageDocument,
  },
  result: {
    data: {
      pendingWorkspaceInvitations: { totalItems: 0, items: [] },
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
});

const workspace = (name: string, generateToken = true) => ({
  __typename: "Workspace",
  slug: name.toLowerCase().replace(/\s/g, "-"),
  name,
  currentMembership: {
    __typename: "WorkspaceMembership",
    role: generateToken ? "EDITOR" : "VIEWER",
  },
  permissions: {
    __typename: "WorkspacePermissions",
    generateToken,
  },
});

// An organization admin who is not a member of the workspace
const administeredWorkspace = (name: string) => ({
  ...workspace(name),
  currentMembership: null,
});

const accessTokensMock = (
  items: object[],
  totalItems: number,
  page = 1,
  perPage = 20,
): MockedResponse => ({
  request: {
    query: AccountAccessTokensDocument,
    variables: { page, perPage },
  },
  result: {
    data: {
      workspaces: {
        __typename: "WorkspacePage",
        totalItems,
        items,
      },
    },
  },
});

describe("AccountPage", () => {
  beforeEach(() => {
    mockRouter.setCurrentUrl("/user/account");
  });

  it("renders without two-factor enabled", async () => {
    render(
      <TestApp mocks={[accountPageMock(), accessTokensMock([], 0)]}>
        <AccountPage />
      </TestApp>,
    );
    const elm = await screen.findByText("Alphonse Brown");
    expect(elm).toBeInTheDocument();

    const securitySection = screen.queryByText("Currently disabled");
    expect(securitySection).toBeInTheDocument();
  });

  it("renders with two-factor enabled and not active for the user", async () => {
    render(
      <TestApp mocks={[accountPageMock(), accessTokensMock([], 0)]}>
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
    const graphqlMocks = [
      accountPageMock(),
      accessTokensMock(
        [workspace("Editor Workspace"), workspace("Viewer Workspace", false)],
        2,
      ),
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
    expect(
      screen.getAllByRole("button", { name: "Show the access token" }),
    ).toHaveLength(1);
    expect(
      screen.getByText("Ask a workspace admin for an editor role."),
    ).toBeInTheDocument();
  });

  it("flags workspaces the user only administers as issuing a temporary token", async () => {
    const graphqlMocks = [
      accountPageMock(),
      accessTokensMock(
        [workspace("Member Workspace"), administeredWorkspace("Admin Only")],
        2,
      ),
    ];

    render(
      <TestApp mocks={graphqlMocks}>
        <AccountPage />
      </TestApp>,
    );

    expect(await screen.findByText("Admin Only")).toBeInTheDocument();
    // Both can generate a token, but only one of them lasts
    expect(
      screen.getAllByRole("button", { name: "Show the access token" }),
    ).toHaveLength(2);
    expect(screen.getByText("Temporary")).toBeInTheDocument();
    // The role column says where the access comes from instead of being empty
    expect(screen.getByText("Organization admin")).toBeInTheDocument();
    expect(screen.queryByText("-")).not.toBeInTheDocument();
  });

  it("pages through the workspaces server-side instead of truncating them", async () => {
    const user = userEvent.setup();
    const firstPage = Array.from({ length: 20 }, (_, i) =>
      workspace(`Workspace ${i + 1}`),
    );
    const graphqlMocks = [
      accountPageMock(),
      accessTokensMock(firstPage, 22),
      accessTokensMock(
        [workspace("Workspace 21"), workspace("Workspace 22")],
        22,
        2,
      ),
    ];

    render(
      <TestApp mocks={graphqlMocks}>
        <AccountPage />
      </TestApp>,
    );

    expect(await screen.findByText("Workspace 1")).toBeInTheDocument();
    expect(screen.queryByText("Workspace 21")).not.toBeInTheDocument();

    await user.click(screen.getAllByRole("button", { name: "Next" })[0]);

    expect(await screen.findByText("Workspace 21")).toBeInTheDocument();
    expect(screen.queryByText("Workspace 1")).not.toBeInTheDocument();
  });

  it("lets a user with many workspaces raise the page size", async () => {
    const user = userEvent.setup();
    const firstPage = Array.from({ length: 20 }, (_, i) =>
      workspace(`Workspace ${i + 1}`),
    );
    const graphqlMocks = [
      accountPageMock(),
      accessTokensMock(firstPage, 22),
      accessTokensMock(
        [...firstPage, workspace("Workspace 21"), workspace("Workspace 22")],
        22,
        1,
        50,
      ),
    ];

    render(
      <TestApp mocks={graphqlMocks}>
        <AccountPage />
      </TestApp>,
    );

    expect(await screen.findByText("Workspace 1")).toBeInTheDocument();
    expect(screen.queryByText("Workspace 22")).not.toBeInTheDocument();

    await user.selectOptions(screen.getByRole("combobox"), "50");

    expect(await screen.findByText("Workspace 22")).toBeInTheDocument();
    expect(screen.getByText("Workspace 1")).toBeInTheDocument();
  });
});

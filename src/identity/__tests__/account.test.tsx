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
    expect(securitySection).not.toBeInTheDocument();
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
              },
            },
          },
        },
      },
    ];

    const { container } = render(
      <TestApp mocks={graphqlMocks} me={{ features: [{ code: "two_factor" }] }}>
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
});

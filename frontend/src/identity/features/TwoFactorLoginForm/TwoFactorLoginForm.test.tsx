import { useApolloClient } from "@apollo/client";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { TestApp } from "core/helpers/testutils";
import { GenerateChallengeDocument } from "identity/graphql/mutations.generated";
import { logout } from "identity/helpers/auth";
import TwoFactorLoginForm from "./TwoFactorLoginForm";

jest.mock("@apollo/client", () => ({
  ...jest.requireActual("@apollo/client"),
  useApolloClient: jest.fn(),
}));

jest.mock("identity/helpers/auth", () => ({
  logout: jest.fn(),
}));

describe("TwoFactorLoginForm", () => {
  it("logs out, then resets the cache so the login page stops showing the code form", async () => {
    const calls: string[] = [];
    (logout as jest.Mock).mockImplementation(async () => {
      calls.push("logout");
    });
    const resetStore = jest.fn(async () => {
      calls.push("resetStore");
    });
    (useApolloClient as jest.Mock).mockReturnValue({ resetStore });
    const user = userEvent.setup();

    render(
      <TestApp
        mocks={[
          {
            request: { query: GenerateChallengeDocument },
            result: {
              data: { generateChallenge: { success: true, errors: null } },
            },
          },
        ]}
      >
        <TwoFactorLoginForm />
      </TestApp>,
    );
    await user.click(
      screen.getByRole("button", { name: "Use another account" }),
    );

    await waitFor(() => expect(calls).toEqual(["logout", "resetStore"]));
  });
});

import { render, screen } from "@testing-library/react";
import { TestApp } from "core/helpers/testutils";
import { useSignupPageQuery } from "identity/graphql/queries.generated";
import mockRouter from "next-router-mock";
import SignupPage from "pages/signup";

jest.mock("identity/graphql/queries.generated", () => ({
  ...jest.requireActual("identity/graphql/queries.generated"),
  __esModule: true,
  useSignupPageQuery: jest.fn(),
}));

const useSignupPageQueryMock = useSignupPageQuery as jest.Mock;

const GOOGLE_PROVIDER = {
  id: "google",
  displayName: "Google",
  loginUrl: "http://localhost:8000/accounts/oidc/google/login/",
};

const mockConfig = (oidcProviders: (typeof GOOGLE_PROVIDER)[]) =>
  useSignupPageQueryMock.mockReturnValue({
    data: {
      config: {
        allowSelfRegistration: true,
        passwordLoginEnabled: true,
        oidcProviders,
      },
    },
    loading: false,
  });

describe("SignupPage", () => {
  beforeEach(() => mockRouter.setCurrentUrl("/signup"));

  it("offers to sign up with an SSO provider", () => {
    mockConfig([GOOGLE_PROVIDER]);
    render(
      <TestApp>
        <SignupPage />
      </TestApp>,
    );

    expect(screen.getByLabelText("Email address")).toBeInTheDocument();
    expect(screen.getByText("or")).toBeInTheDocument();
    expect(screen.getByRole("link", { name: /sign up with/i })).toHaveAttribute(
      "href",
      `${GOOGLE_PROVIDER.loginUrl}?next=${encodeURIComponent("/workspaces")}`,
    );
  });

  it("shows only the email form without SSO providers", () => {
    mockConfig([]);
    render(
      <TestApp>
        <SignupPage />
      </TestApp>,
    );

    expect(screen.getByLabelText("Email address")).toBeInTheDocument();
    expect(screen.queryByText("or")).not.toBeInTheDocument();
    expect(screen.queryByRole("link", { name: /sign up with/i })).toBeNull();
  });
});

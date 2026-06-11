import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { TestApp } from "core/helpers/testutils";
import {
  LoginDocument,
  useLoginMutation,
} from "identity/graphql/mutations.generated";
import { useSignupPageQuery } from "identity/graphql/queries.generated";
import mockRouter from "next-router-mock";
import router from "next/router";
import LoginPage from "pages/login";

jest.mock("identity/graphql/mutations.generated", () => {
  const actualModule = jest.requireActual(
    "identity/graphql/mutations.generated",
  );
  return {
    ...actualModule,
    __esModule: true,
    useLoginMutation: jest.fn(actualModule.useLoginMutation),
  };
});

jest.mock("identity/graphql/queries.generated", () => ({
  ...jest.requireActual("identity/graphql/queries.generated"),
  __esModule: true,
  useSignupPageQuery: jest.fn(() => ({
    data: {
      config: {
        allowSelfRegistration: false,
        passwordLoginEnabled: true,
        oidcProviders: [],
      },
    },
    loading: false,
  })),
}));

const useLoginMutationMock = useLoginMutation as jest.Mock;
const useSignupPageQueryMock = useSignupPageQuery as jest.Mock;

const DEFAULT_CONFIG = {
  data: {
    config: {
      allowSelfRegistration: false,
      passwordLoginEnabled: true,
      oidcProviders: [],
    },
  },
  loading: false,
};

const WHO_PROVIDER = {
  id: "who",
  displayName: "WHO",
  loginUrl: "http://localhost:8000/accounts/oidc/who/login/",
};
describe("LoginPage: No Two Factor Authentication", () => {
  beforeEach(() => {
    mockRouter.setCurrentUrl("/");
    useLoginMutationMock.mockClear();
  });

  it("renders the login page", async () => {
    const { container } = render(
      <TestApp>
        <LoginPage />
      </TestApp>,
    );

    expect(container).toMatchSnapshot();
  });

  it("calls the login action on submit", async () => {
    const doLogin = jest.fn();
    useLoginMutationMock.mockReturnValue([doLogin]);
    const user = userEvent.setup();
    const { container } = render(
      <TestApp>
        <LoginPage />
      </TestApp>,
    );

    const emailInput = screen.getByTestId("email");
    const passwordInput = screen.getByTestId("password");
    const submitBtn = screen.getByRole("button", { name: "Sign in" });

    await user.type(emailInput, "root@openhexa.org");
    await user.click(submitBtn);
    expect(doLogin).not.toHaveBeenCalled();

    await user.type(passwordInput, "pA$$W0rd");
    await user.click(submitBtn);
    expect(useLoginMutation).toHaveBeenCalled();
    expect(doLogin).toHaveBeenCalledWith({
      variables: {
        input: {
          email: "root@openhexa.org",
          password: "pA$$W0rd",
          token: undefined,
        },
      },
    });
  });

  it("redirects the user on success", async () => {
    const pushSpy = jest.spyOn(router, "push");
    const { useLoginMutation } = jest.requireActual(
      "identity/graphql/mutations.generated",
    );
    useLoginMutationMock.mockImplementation(useLoginMutation);
    const user = userEvent.setup();
    const mocks = [
      {
        request: {
          query: LoginDocument,
          variables: {
            input: {
              email: "root@openhexa.org",
            },
          },
        },
        result: {
          data: { login: { success: true } },
        },
      },
    ];
    expect(useLoginMutationMock).not.toHaveBeenCalled();
    render(
      <TestApp mocks={mocks}>
        <LoginPage />
      </TestApp>,
    );
    expect(useLoginMutationMock).toHaveBeenCalled();

    const emailInput = screen.getByTestId("email");
    const passwordInput = screen.getByTestId("password");
    const submitBtn = screen.getByRole("button", { name: "Sign in" });

    await user.type(emailInput, "root@openhexa.org");
    await user.click(submitBtn);
    expect(pushSpy).not.toHaveBeenCalled();
    await user.type(passwordInput, "pA$$W0rd");
    await user.click(submitBtn);
    waitFor(() => {
      expect(pushSpy).toHaveBeenCalled();
    });
  });

  it("displays an error message if email/password is incorrect", async () => {
    const { useLoginMutation } = jest.requireActual(
      "identity/graphql/mutations.generated",
    );
    useLoginMutationMock.mockImplementation(useLoginMutation);
    const user = userEvent.setup();
    const [EMAIL, PWD] = ["root@openhexa.org", "pA$$W0rd"];
    const mocks = [
      {
        request: {
          query: LoginDocument,
          variables: {
            input: {
              email: EMAIL,
              password: PWD,
            },
          },
        },
        result: {
          data: { login: { success: false, errors: ["INVALID_CREDENTIALS"] } },
        },
      },
    ];
    render(
      <TestApp mocks={mocks}>
        <LoginPage />
      </TestApp>,
    );

    const emailInput = screen.getByTestId("email");
    const passwordInput = screen.getByTestId("password");
    const submitBtn = screen.getByRole("button", { name: "Sign in" });
    await user.type(emailInput, EMAIL);
    await user.type(passwordInput, PWD);
    await user.click(submitBtn);
    const errorMessage = await screen.findByText(
      "Wrong email address and/or password.",
    );

    expect(errorMessage).toBeInTheDocument();
  });
});

describe("LoginPage: Loading state", () => {
  beforeEach(() => {
    mockRouter.setCurrentUrl("/");
    useSignupPageQueryMock.mockReturnValue({ data: undefined, loading: true });
  });

  afterEach(() => {
    useSignupPageQueryMock.mockReturnValue(DEFAULT_CONFIG);
  });

  it("shows a spinner and no form while config is loading", () => {
    render(
      <TestApp>
        <LoginPage />
      </TestApp>,
    );

    expect(screen.getByTestId("spinner")).toBeInTheDocument();
    expect(screen.queryByTestId("email")).not.toBeInTheDocument();
    expect(screen.queryByTestId("password")).not.toBeInTheDocument();
  });
});

describe("LoginPage: SSO-only (password login disabled)", () => {
  beforeEach(() => {
    mockRouter.setCurrentUrl("/");
    useSignupPageQueryMock.mockReturnValue({
      data: {
        config: {
          allowSelfRegistration: false,
          passwordLoginEnabled: false,
          oidcProviders: [WHO_PROVIDER],
        },
      },
      loading: false,
    });
  });

  afterEach(() => {
    useSignupPageQueryMock.mockReturnValue(DEFAULT_CONFIG);
  });

  it("shows SSO button and hides the password form", () => {
    render(
      <TestApp>
        <LoginPage />
      </TestApp>,
    );

    expect(
      screen.getByRole("link", { name: /sign in with/i }),
    ).toBeInTheDocument();
    expect(screen.queryByTestId("email")).not.toBeInTheDocument();
    expect(screen.queryByTestId("password")).not.toBeInTheDocument();
    expect(
      screen.queryByRole("button", { name: "Sign in" }),
    ).not.toBeInTheDocument();
  });

  it("SSO link points to the provider login URL with next param", () => {
    mockRouter.setCurrentUrl("/login?next=%2Fdashboard");
    render(
      <TestApp>
        <LoginPage />
      </TestApp>,
    );

    const link = screen.getByRole("link", { name: /sign in with/i });
    expect(link).toHaveAttribute(
      "href",
      `${WHO_PROVIDER.loginUrl}?next=%2Fdashboard`,
    );
  });
});

describe("LoginPage: Mixed mode (password + SSO)", () => {
  beforeEach(() => {
    mockRouter.setCurrentUrl("/");
    useSignupPageQueryMock.mockReturnValue({
      data: {
        config: {
          allowSelfRegistration: false,
          passwordLoginEnabled: true,
          oidcProviders: [WHO_PROVIDER],
        },
      },
      loading: false,
    });
  });

  afterEach(() => {
    useSignupPageQueryMock.mockReturnValue(DEFAULT_CONFIG);
  });

  it("shows the password form, the or divider, and the SSO button", () => {
    render(
      <TestApp>
        <LoginPage />
      </TestApp>,
    );

    expect(screen.getByTestId("email")).toBeInTheDocument();
    expect(screen.getByTestId("password")).toBeInTheDocument();
    expect(screen.getByText("or")).toBeInTheDocument();
    expect(
      screen.getByRole("link", { name: /sign in with/i }),
    ).toBeInTheDocument();
  });
});

describe("LoginPage: With Two Factor Authentication", () => {
  beforeEach(() => {
    mockRouter.setCurrentUrl("/");
    useLoginMutationMock.mockImplementation(useLoginMutation);
  });

  it("asks for a token after a login attempt", async () => {
    const doLogin = jest.fn(() => ({
      data: {
        login: { success: false, errors: ["OTP_REQUIRED"] },
      },
    }));
    useLoginMutationMock.mockReturnValue([doLogin]);
    expect(doLogin).not.toHaveBeenCalled();
    const user = userEvent.setup();
    const [EMAIL, PWD] = ["root@openhexa.org", "pA$$W0rd"];

    render(
      <TestApp me={{ hasTwoFactorEnabled: true }}>
        <LoginPage />
      </TestApp>,
    );

    const emailInput = screen.getByTestId("email");
    const passwordInput = screen.getByTestId("password");
    const submitBtn = screen.getByRole("button", { name: "Sign in" });
    await user.type(emailInput, EMAIL);
    await user.type(passwordInput, PWD);
    await user.click(submitBtn);
    expect(doLogin).toHaveBeenCalled();

    const message = await screen.findByText(
      "Enter the OTP code you received in your mailbox.",
    );
    expect(message).toBeInTheDocument();

    const tokenInput = screen.getByTestId("token");
    expect(tokenInput).toBeInTheDocument();
    await user.type(tokenInput, "121212");
    await user.click(submitBtn);

    expect(doLogin).toHaveBeenLastCalledWith({
      variables: {
        input: {
          email: EMAIL,
          password: PWD,
          token: "121212",
        },
      },
    });
  });
});

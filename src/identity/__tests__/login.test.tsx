import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { TestApp } from "core/helpers/testutils";
import {
  LoginDocument,
  useLoginMutation,
} from "identity/graphql/mutations.generated";
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

const useLoginMutationMock = useLoginMutation as jest.Mock;
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

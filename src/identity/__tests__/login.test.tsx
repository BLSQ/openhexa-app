import { MockedResponse } from "@apollo/client/testing";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import {
  LoginDocument,
  useLoginMutation,
} from "core/graphql/mutations.generated";
import { TestApp } from "core/helpers/testutils";
import mockRouter from "next-router-mock";
import router from "next/router";
import LoginPage from "pages/index";

jest.mock("core/graphql/mutations.generated", () => ({
  ...jest.requireActual("core/graphql/mutations.generated"),
  __esModule: true,
  useLoginMutation: jest.fn().mockReturnValue([]),
}));

const useLoginMutationMock = useLoginMutation as jest.Mock;
describe("LoginPage", () => {
  beforeEach(() => {
    mockRouter.setCurrentUrl("/");
    useLoginMutationMock.mockClear();
  });

  it("renders the login page", async () => {
    const graphqlMocks: MockedResponse[] = [];
    const { container } = render(
      <TestApp mocks={graphqlMocks}>
        <LoginPage />
      </TestApp>
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
      </TestApp>
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
        input: { email: "root@openhexa.org", password: "pA$$W0rd" },
      },
    });
  });

  it("redirects the user on success", async () => {
    const pushSpy = jest.spyOn(router, "push");
    const { useLoginMutation } = jest.requireActual(
      "core/graphql/mutations.generated"
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
      </TestApp>
    );
    expect(useLoginMutationMock).toHaveBeenCalled();

    const emailInput = screen.getByTestId("email");
    const passwordInput = screen.getByTestId("password");
    const submitBtn = screen.getByRole("button", { name: "Sign in" });

    expect(submitBtn).toBeDisabled();
    await user.type(emailInput, "root@openhexa.org");
    await user.click(submitBtn);
    expect(pushSpy).not.toHaveBeenCalled();
    await user.type(passwordInput, "pA$$W0rd");
    expect(submitBtn).not.toBeDisabled();
    await user.click(submitBtn);
    waitFor(() => {
      expect(pushSpy).toHaveBeenCalled();
    });
  });

  it("displays an error message if email/password is incorrect", async () => {
    const { useLoginMutation } = jest.requireActual(
      "core/graphql/mutations.generated"
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
          data: { login: { success: false } },
        },
      },
    ];
    render(
      <TestApp mocks={mocks}>
        <LoginPage />
      </TestApp>
    );

    const emailInput = screen.getByTestId("email");
    const passwordInput = screen.getByTestId("password");
    const submitBtn = screen.getByRole("button", { name: "Sign in" });
    await user.type(emailInput, EMAIL);
    await user.type(passwordInput, PWD);
    await user.click(submitBtn);
    const errorMessage = await screen.findByText(
      "Wrong email address and/or password."
    );

    expect(errorMessage).toBeInTheDocument();
  });
});

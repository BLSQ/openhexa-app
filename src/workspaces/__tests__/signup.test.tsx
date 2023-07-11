import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import {
  JoinWorkspaceDocument,
  useJoinWorkspaceMutation,
} from "workspaces/graphql/mutations.generated";
import { TestApp } from "core/helpers/testutils";
import mockRouter from "next-router-mock";
import router from "next/router";
import SignUpPage from "pages/workspaces/[workspaceSlug]/signup";
import { faker } from "@faker-js/faker";

const USER = {
  email: faker.internet.email(),
  firstName: faker.name.firstName(),
  lastName: faker.name.lastName(),
  token: faker.datatype.string(20),
};

jest.mock("workspaces/graphql/mutations.generated", () => {
  const actualModule = jest.requireActual(
    "workspaces/graphql/mutations.generated"
  );
  return {
    ...actualModule,
    __esModule: true,
    useJoinWorkspaceMutation: jest.fn(actualModule.useJoinWorkspaceMutation),
  };
});

//

const useJoinWorkspaceMutationMock = useJoinWorkspaceMutation as jest.Mock;
describe("WorkspaceSignUpPage", () => {
  beforeEach(() => {
    mockRouter.setCurrentUrl("/");
    useJoinWorkspaceMutationMock.mockClear();
  });

  it("renders the sign up page", async () => {
    const { container } = render(
      <TestApp>
        <SignUpPage />
      </TestApp>
    );

    expect(container).toMatchSnapshot();
  });

  it("calls the join workspace action when form is correctly filled", async () => {
    const joinWorkspace = jest.fn();
    useJoinWorkspaceMutationMock.mockReturnValue([joinWorkspace]);
    const user = userEvent.setup();

    render(
      <TestApp>
        <SignUpPage email={USER.email} token={USER.token} />
      </TestApp>
    );

    const submitBtn = screen.getByRole("button", { name: "Submit" });

    await user.click(submitBtn);
    expect(joinWorkspace).not.toHaveBeenCalled();

    const firstName = screen.getByTestId("firstName");
    await user.type(firstName, USER.firstName);
    await user.click(submitBtn);
    expect(joinWorkspace).not.toHaveBeenCalled();

    const lastName = screen.getByTestId("lastName");
    await user.type(lastName, USER.lastName);
    await user.click(submitBtn);
    expect(joinWorkspace).not.toHaveBeenCalled();

    const password = screen.getByTestId("password");
    await user.type(password, "pA$$W0rd");
    await user.click(submitBtn);
    expect(joinWorkspace).not.toHaveBeenCalled();

    const confirmPassword = screen.getByTestId("confirmPassword");
    await user.type(confirmPassword, "foo@bar");
    await user.click(submitBtn);

    expect(joinWorkspace).not.toHaveBeenCalled();
    const errorMessage = await screen.findByText(
      "The password confirmation does not match the given password"
    );
    expect(errorMessage).toBeInTheDocument();

    await user.clear(confirmPassword);
    await user.type(confirmPassword, "pA$$W0rd");
    await user.click(submitBtn);

    expect(joinWorkspace).toHaveBeenCalled();
    expect(joinWorkspace).toHaveBeenCalledWith({
      variables: {
        input: {
          firstName: USER.firstName,
          lastName: USER.lastName,
          token: USER.token,
          password: "pA$$W0rd",
          confirmPassword: "pA$$W0rd",
        },
      },
    });
  });

  it("redirects the user on success", async () => {
    const pushSpy = jest.spyOn(router, "push");
    const { useJoinWorkspaceMutation } = jest.requireActual(
      "workspaces/graphql/mutations.generated"
    );
    useJoinWorkspaceMutationMock.mockImplementation(useJoinWorkspaceMutation);
    const user = userEvent.setup();
    const mocks = [
      {
        request: {
          query: JoinWorkspaceDocument,
          variables: {
            input: {
              firstName: USER.firstName,
              lastName: USER.lastName,
              token: USER.token,
              password: "pA$$W0rd",
              confirmPassword: "pA$$W0rd",
            },
          },
        },
        result: {
          data: {
            joinWorkspace: {
              success: true,
              errors: [],
              workspace: {
                slug: "slug",
              },
            },
          },
        },
      },
    ];

    render(
      <TestApp mocks={mocks}>
        <SignUpPage email={USER.email} token={USER.token} />
      </TestApp>
    );

    const submitBtn = screen.getByRole("button", { name: "Submit" });

    await user.click(submitBtn);
    expect(pushSpy).not.toHaveBeenCalled();

    const firstName = screen.getByTestId("firstName");
    const lastName = screen.getByTestId("lastName");
    const password = screen.getByTestId("password");
    const confirmPassword = screen.getByTestId("confirmPassword");

    await user.type(firstName, USER.firstName);
    await user.type(lastName, USER.lastName);
    await user.type(password, "pA$$W0rd");
    await user.type(confirmPassword, "pA$$W0rd");

    await user.click(submitBtn);

    waitFor(() => {
      expect(pushSpy).toHaveBeenCalled();
    });
  });

  it("displays invalid password formet error message when the password is similar to user info", async () => {
    const pushSpy = jest.spyOn(router, "push");
    const { useJoinWorkspaceMutation } = jest.requireActual(
      "workspaces/graphql/mutations.generated"
    );
    useJoinWorkspaceMutationMock.mockImplementation(useJoinWorkspaceMutation);
    const user = userEvent.setup();
    const mocks = [
      {
        request: {
          query: JoinWorkspaceDocument,
          variables: {
            input: {
              firstName: USER.firstName,
              lastName: USER.lastName,
              token: USER.token,
              password: USER.firstName,
              confirmPassword: USER.firstName,
            },
          },
        },
        result: {
          data: {
            joinWorkspace: {
              success: false,
              errors: ["INVALID_CREDENTIALS"],
              workspace: null,
            },
          },
        },
      },
    ];

    render(
      <TestApp mocks={mocks}>
        <SignUpPage email={USER.email} token={USER.token} />
      </TestApp>
    );

    const submitBtn = screen.getByRole("button", { name: "Submit" });

    await user.click(submitBtn);
    expect(pushSpy).not.toHaveBeenCalled();

    const firstName = screen.getByTestId("firstName");
    const lastName = screen.getByTestId("lastName");
    const password = screen.getByTestId("password");
    const confirmPassword = screen.getByTestId("confirmPassword");

    await user.type(firstName, USER.firstName);
    await user.type(lastName, USER.lastName);
    await user.type(password, USER.firstName);
    await user.type(confirmPassword, USER.firstName);
    await user.click(submitBtn);

    const errorMessage = await screen.findByText("Invalid password format");
    expect(errorMessage).toBeInTheDocument();
  });

  it("displays an invalid token error message when the token format is not correct or not linked to an invitation", async () => {
    const pushSpy = jest.spyOn(router, "push");
    const { useJoinWorkspaceMutation } = jest.requireActual(
      "workspaces/graphql/mutations.generated"
    );
    useJoinWorkspaceMutationMock.mockImplementation(useJoinWorkspaceMutation);
    const user = userEvent.setup();
    const mocks = [
      {
        request: {
          query: JoinWorkspaceDocument,
          variables: {
            input: {
              firstName: USER.firstName,
              lastName: USER.lastName,
              token: "123",
              password: "pA$$W0rd",
              confirmPassword: "pA$$W0rd",
            },
          },
        },
        result: {
          data: {
            joinWorkspace: {
              success: false,
              errors: ["INVALID_TOKEN"],
              workspace: null,
            },
          },
        },
      },
    ];

    render(
      <TestApp mocks={mocks}>
        <SignUpPage email={USER.email} token={"123"} />
      </TestApp>
    );

    const submitBtn = screen.getByRole("button", { name: "Submit" });

    await user.click(submitBtn);
    expect(pushSpy).not.toHaveBeenCalled();

    const firstName = screen.getByTestId("firstName");
    const lastName = screen.getByTestId("lastName");
    const password = screen.getByTestId("password");
    const confirmPassword = screen.getByTestId("confirmPassword");

    await user.type(firstName, USER.firstName);
    await user.type(lastName, USER.lastName);
    await user.type(password, "pA$$W0rd");
    await user.type(confirmPassword, "pA$$W0rd");
    await user.click(submitBtn);

    const errorMessage = await screen.findByText("The invite link is invalid.");
    expect(errorMessage).toBeInTheDocument();
  });

  it("displays expired invitation error message when the token is expired", async () => {
    const pushSpy = jest.spyOn(router, "push");
    const { useJoinWorkspaceMutation } = jest.requireActual(
      "workspaces/graphql/mutations.generated"
    );
    useJoinWorkspaceMutationMock.mockImplementation(useJoinWorkspaceMutation);
    const user = userEvent.setup();
    const mocks = [
      {
        request: {
          query: JoinWorkspaceDocument,
          variables: {
            input: {
              firstName: USER.firstName,
              lastName: USER.lastName,
              token: USER.token,
              password: "pA$$W0rd",
              confirmPassword: "pA$$W0rd",
            },
          },
        },
        result: {
          data: {
            joinWorkspace: {
              success: false,
              errors: ["EXPIRED_TOKEN"],
              workspace: null,
            },
          },
        },
      },
    ];

    render(
      <TestApp mocks={mocks}>
        <SignUpPage email={USER.email} token={USER.token} />
      </TestApp>
    );

    const submitBtn = screen.getByRole("button", { name: "Submit" });

    await user.click(submitBtn);
    expect(pushSpy).not.toHaveBeenCalled();

    const firstName = screen.getByTestId("firstName");
    const lastName = screen.getByTestId("lastName");
    const password = screen.getByTestId("password");
    const confirmPassword = screen.getByTestId("confirmPassword");

    await user.type(firstName, USER.firstName);
    await user.type(lastName, USER.lastName);
    await user.type(password, "pA$$W0rd");
    await user.type(confirmPassword, "pA$$W0rd");
    await user.click(submitBtn);

    const errorMessage = await screen.findByText("The invitation has expired.");
    expect(errorMessage).toBeInTheDocument();
  });

  it("displays account already exists error message when the user has already an account", async () => {
    const pushSpy = jest.spyOn(router, "push");
    const { useJoinWorkspaceMutation } = jest.requireActual(
      "workspaces/graphql/mutations.generated"
    );
    useJoinWorkspaceMutationMock.mockImplementation(useJoinWorkspaceMutation);
    const user = userEvent.setup();
    const mocks = [
      {
        request: {
          query: JoinWorkspaceDocument,
          variables: {
            input: {
              firstName: USER.firstName,
              lastName: USER.lastName,
              token: USER.token,
              password: "pA$$W0rd",
              confirmPassword: "pA$$W0rd",
            },
          },
        },
        result: {
          data: {
            joinWorkspace: {
              success: false,
              errors: ["ALREADY_EXISTS"],
              workspace: null,
            },
          },
        },
      },
    ];

    render(
      <TestApp mocks={mocks}>
        <SignUpPage email={USER.email} token={USER.token} />
      </TestApp>
    );

    const submitBtn = screen.getByRole("button", { name: "Submit" });

    await user.click(submitBtn);
    expect(pushSpy).not.toHaveBeenCalled();

    const firstName = screen.getByTestId("firstName");
    const lastName = screen.getByTestId("lastName");
    const password = screen.getByTestId("password");
    const confirmPassword = screen.getByTestId("confirmPassword");

    await user.type(firstName, USER.firstName);
    await user.type(lastName, USER.lastName);
    await user.type(password, "pA$$W0rd");
    await user.type(confirmPassword, "pA$$W0rd");
    await user.click(submitBtn);

    const errorMessage = await screen.findByText(
      "An account already exists with this email address. Please go to the login page."
    );
    expect(errorMessage).toBeInTheDocument();
  });
});

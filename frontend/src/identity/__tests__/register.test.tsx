import { render, screen } from "@testing-library/react";
import { TestApp } from "core/helpers/testutils";
import userEvent from "@testing-library/user-event";
import mockRouter from "next-router-mock";
import RegisterPage from "pages/register";
import { useRegisterMutation } from "identity/graphql/mutations.generated";
import { UserEvent } from "@testing-library/user-event/dist/types/setup/setup";

const useRegisterMutationMock = useRegisterMutation as jest.Mock;

jest.mock("identity/graphql/mutations.generated", () => {
  const actualModule = jest.requireActual(
    "identity/graphql/mutations.generated",
  );
  return {
    ...actualModule,
    __esModule: true,
    useRegisterMutation: jest.fn(actualModule.useRegisterMutation),
  };
});

describe("RegisterPage", () => {
  beforeEach(() => {
    mockRouter.setCurrentUrl("/");
    useRegisterMutationMock.mockClear();
  });

  async function fillRegisterForm(
    user: UserEvent,
    firstName = "John",
    lastName = "Doe",
    password = "pA$$W0rd",
    confirmPassword = "pA$$W0rd",
  ) {
    await user.type(screen.getByLabelText("First name"), firstName);
    await user.type(screen.getByLabelText("Last name"), lastName);
    await user.type(screen.getByLabelText("Password"), password);
    await user.type(screen.getByLabelText("Confirm Password"), confirmPassword);
  }

  it("renders", async () => {
    const { container, debug } = render(
      <TestApp>
        <RegisterPage />
      </TestApp>,
    );

    expect(screen.getByRole("heading", { name: "Create your account" }));
  });

  it("calls the register action on submit", async () => {
    const user = userEvent.setup();
    const doRegister = jest
      .fn()
      .mockReturnValue({ data: { register: { success: true } } });
    useRegisterMutationMock.mockReturnValue([doRegister]);
    const { container } = render(
      <TestApp>
        <RegisterPage token={"REGISTER_TOKEN"} />
      </TestApp>,
    );

    const submitBtn = screen.getByRole("button", { name: "Create account" });
    await fillRegisterForm(user);
    await user.click(submitBtn);
    expect(doRegister).toHaveBeenCalledWith({
      variables: {
        input: {
          firstName: "John",
          lastName: "Doe",
          password1: "pA$$W0rd",
          password2: "pA$$W0rd",
          invitationToken: "REGISTER_TOKEN",
        },
      },
    });
    expect(mockRouter).toMatchObject({ asPath: "/user/account" });
  });

  it("displays an error message when the passwords do not match", async () => {
    const user = userEvent.setup();
    const doRegister = jest
      .fn()
      .mockReturnValue({ data: { register: { success: true } } });
    useRegisterMutationMock.mockReturnValue([doRegister]);
    const { container } = render(
      <TestApp>
        <RegisterPage token={"REGISTER_TOKEN"} />
      </TestApp>,
    );

    const submitBtn = screen.getByRole("button", { name: "Create account" });
    await fillRegisterForm(user, "John", "Doe", "pA$$W0rd", "pA$$W0rd2");
    await user.click(submitBtn);
    expect(doRegister).not.toHaveBeenCalled();
    expect(
      screen.getByText("The two passwords are not the same"),
    ).toBeInTheDocument();
  });

  it("displays an error message when the passwords are not valid for the server", async () => {
    const user = userEvent.setup();
    const doRegister = jest.fn().mockReturnValue({
      data: {
        register: {
          success: false,
          errors: ["INVALID_PASSWORD"],
        },
      },
    });
    useRegisterMutationMock.mockReturnValue([doRegister]);
    const { container } = render(
      <TestApp>
        <RegisterPage token={"REGISTER_TOKEN"} />
      </TestApp>,
    );

    const submitBtn = screen.getByRole("button", { name: "Create account" });
    await fillRegisterForm(user);
    await user.click(submitBtn);
    expect(doRegister).toHaveBeenCalled();
    expect(screen.getByText("Invalid password")).toBeInTheDocument();
  });

  it("displays an error message when the invitation token is invalid", async () => {
    const user = userEvent.setup();
    const doRegister = jest.fn().mockReturnValue({
      data: {
        register: {
          success: false,
          errors: ["INVALID_TOKEN"],
        },
      },
    });
    useRegisterMutationMock.mockReturnValue([doRegister]);
    const { container } = render(
      <TestApp>
        <RegisterPage token={"REGISTER_TOKEN"} />
      </TestApp>,
    );

    const submitBtn = screen.getByRole("button", { name: "Create account" });
    await fillRegisterForm(user);
    await user.click(submitBtn);
    expect(doRegister).toHaveBeenCalled();
    expect(
      screen.getByText(
        "You cannot register an account with this link. Please contact the person that invited you to receive a new link.",
      ),
    ).toBeInTheDocument();
  });

  it("displays an error message when the email is already taken", async () => {
    const user = userEvent.setup();
    const doRegister = jest.fn().mockReturnValue({
      data: {
        register: {
          success: false,
          errors: ["EMAIL_TAKEN"],
        },
      },
    });
    useRegisterMutationMock.mockReturnValue([doRegister]);
    const { container } = render(
      <TestApp>
        <RegisterPage token={"REGISTER_TOKEN"} />
      </TestApp>,
    );

    const submitBtn = screen.getByRole("button", { name: "Create account" });
    await fillRegisterForm(user);
    await user.click(submitBtn);
    expect(doRegister).toHaveBeenCalled();
    expect(
      screen.getByText(
        "This email address is already taken. Please login instead.",
      ),
    ).toBeInTheDocument();
  });
});

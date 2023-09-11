import DisableTwoFactorDialog from "./DisableTwoFactorDialog";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { TestApp } from "core/helpers/testutils";
import { disableTwoFactor, generateChallenge } from "identity/helpers/auth";

jest.mock("identity/helpers/auth", () => ({
  __esModule: true,
  ...jest.requireActual("identity/helpers/auth"),
  generateChallenge: jest.fn(),
  disableTwoFactor: jest.fn(),
}));

const generateChallengeMock = generateChallenge as jest.Mock;
const disableTwoFactorMock = disableTwoFactor as jest.Mock;

describe("DisableTwoFactorDialog", () => {
  beforeEach(() => {
    generateChallengeMock.mockClear();
    disableTwoFactorMock.mockClear();
    generateChallengeMock.mockReturnValue(true);
    disableTwoFactorMock.mockReturnValue({
      disableTwoFactor: { success: true },
    });
  });
  it("displays an alert if user is not verified", async () => {
    const onClose = jest.fn();
    const { container } = render(
      <TestApp>
        <DisableTwoFactorDialog open onClose={onClose} />
      </TestApp>,
    );
    const alertText = await screen.findByText(
      "Two-Factor Authentication is not enabled for your account",
    );
    expect(alertText).toBeInTheDocument();
  });

  it("disables the two factor for the user", async () => {
    const user = userEvent.setup();
    const onClose = jest.fn();
    const { container } = render(
      <TestApp
        me={{ features: [{ code: "two_factor" }], hasTwoFactorEnabled: true }}
      >
        <DisableTwoFactorDialog open onClose={onClose} />
      </TestApp>,
    );
    expect(generateChallengeMock).not.toHaveBeenCalled();
    expect(disableTwoFactorMock).not.toHaveBeenCalled();
    const alertText = await screen.findByText(
      "Are you sure to disable the two-factor authentication for your account?",
    );
    expect(alertText).toBeInTheDocument();

    await user.click(screen.getByText("Disable", { selector: "button" }));
    expect(generateChallengeMock).toHaveBeenCalled();
    expect(
      screen.getByText(
        "Check your inbox and type the token you received to disable the two-factor authentication.",
      ),
    ).toBeInTheDocument();
    const inputElement = await screen.getByPlaceholderText("123456");
    await user.type(inputElement, "999999");
    await user.click(screen.getByText("Disable", { selector: "button" }));

    expect(disableTwoFactorMock).toHaveBeenCalledWith("999999");
    expect(onClose).toHaveBeenCalled();
  });

  it("does nothing without the token", async () => {
    const user = userEvent.setup();
    const onClose = jest.fn();
    const { container } = render(
      <TestApp
        me={{ features: [{ code: "two_factor" }], hasTwoFactorEnabled: true }}
      >
        <DisableTwoFactorDialog open onClose={onClose} />
      </TestApp>,
    );
    expect(generateChallengeMock).not.toHaveBeenCalled();
    expect(disableTwoFactorMock).not.toHaveBeenCalled();
    const alertText = await screen.findByText(
      "Are you sure to disable the two-factor authentication for your account?",
    );
    expect(alertText).toBeInTheDocument();

    await user.click(screen.getByText("Disable", { selector: "button" }));
    expect(generateChallengeMock).toHaveBeenCalled();
    expect(
      screen.getByText(
        "Check your inbox and type the token you received to disable the two-factor authentication.",
      ),
    ).toBeInTheDocument();
    const btn = screen.getByText("Disable", { selector: "button" });
    expect(btn).toBeDisabled();

    await user.click(btn);

    expect(disableTwoFactorMock).not.toHaveBeenCalledWith("999999");
    expect(onClose).not.toHaveBeenCalled();
  });
});

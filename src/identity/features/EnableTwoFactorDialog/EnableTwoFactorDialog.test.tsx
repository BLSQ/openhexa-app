import EnableTwoFactorDialog from "./EnableTwoFactorDialog";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { TestApp } from "core/helpers/testutils";
import { enableTwoFactor, generateChallenge } from "identity/helpers/auth";

jest.mock("identity/helpers/auth", () => ({
  __esModule: true,
  ...jest.requireActual("identity/helpers/auth"),
  enableTwoFactor: jest.fn(),
}));

const enableTwoFactorMock = enableTwoFactor as jest.Mock;

describe("EnableTwoFactorDialog", () => {
  beforeEach(() => {
    enableTwoFactorMock.mockClear();
  });
  it("displays an alert if user has Two-factor devices", async () => {
    const onClose = jest.fn();
    const { container } = render(
      <TestApp
        me={{ features: [{ code: "two_factor" }], hasTwoFactorEnabled: true }}
      >
        <EnableTwoFactorDialog open onClose={onClose} />
      </TestApp>
    );
    const alertText = await screen.findByText(
      "Two-Factor Authentication is already enabled for your account."
    );
    expect(alertText).toBeInTheDocument();
  });

  it("enables the user on submit", async () => {
    const user = userEvent.setup();
    const onClose = jest.fn();
    const { container } = render(
      <TestApp
        me={{ features: [{ code: "two_factor" }], hasTwoFactorEnabled: false }}
      >
        <EnableTwoFactorDialog open onClose={onClose} />
      </TestApp>
    );
    expect(enableTwoFactorMock).not.toHaveBeenCalled();

    await user.click(await screen.findByText("Enable", { selector: "button" }));

    expect(enableTwoFactorMock).toHaveBeenCalled();
    expect(onClose).toHaveBeenCalled();
  });

  it("does nothing on click on 'cancel'", async () => {
    const user = userEvent.setup();
    const onClose = jest.fn();
    const { container } = render(
      <TestApp
        me={{ features: [{ code: "two_factor" }], hasTwoFactorEnabled: false }}
      >
        <EnableTwoFactorDialog open onClose={onClose} />
      </TestApp>
    );
    expect(enableTwoFactorMock).not.toHaveBeenCalled();

    await user.click(await screen.findByText("Cancel", { selector: "button" }));

    expect(enableTwoFactorMock).not.toHaveBeenCalled();
    expect(onClose).toHaveBeenCalled();
  });
});

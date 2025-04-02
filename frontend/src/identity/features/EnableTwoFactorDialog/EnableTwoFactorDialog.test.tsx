import EnableTwoFactorDialog from "./EnableTwoFactorDialog";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { TestApp } from "core/helpers/testutils";
import { enableTwoFactor, verifyDevice } from "identity/helpers/auth";
import router from "next/router";

jest.mock("identity/helpers/auth", () => ({
  __esModule: true,
  ...jest.requireActual("identity/helpers/auth"),
  enableTwoFactor: jest.fn().mockReturnValue({ success: true, verified: true }),
  verifyDevice: jest.fn(),
}));

const enableTwoFactorMock = enableTwoFactor as jest.Mock;
const verifyDeviceMock = verifyDevice as jest.Mock;

describe("EnableTwoFactorDialog", () => {
  beforeEach(() => {
    enableTwoFactorMock.mockClear();
    verifyDeviceMock.mockReset();
  });
  it("displays an alert if user has Two-factor devices", async () => {
    const onClose = jest.fn();
    const { container } = render(
      <TestApp
        me={{ features: [{ code: "two_factor" }], hasTwoFactorEnabled: true }}
      >
        <EnableTwoFactorDialog open onClose={onClose} />
      </TestApp>,
    );
    const alertText = await screen.findByText(
      "Two-Factor Authentication is already enabled for your account.",
    );
    expect(alertText).toBeInTheDocument();
  });

  it("enables the user on submit for non interactive otp", async () => {
    const user = userEvent.setup();
    const onClose = jest.fn();
    const reload = jest.spyOn(router, "reload");
    const { container } = render(
      <TestApp
        me={{ features: [{ code: "two_factor" }], hasTwoFactorEnabled: false }}
      >
        <EnableTwoFactorDialog open onClose={onClose} />
      </TestApp>,
    );
    expect(enableTwoFactorMock).not.toHaveBeenCalled();

    await user.click(await screen.findByText("Enable", { selector: "button" }));

    expect(enableTwoFactorMock).toHaveBeenCalled();
    expect(reload).toHaveBeenCalled();
  });

  it("asks for a token when user enables OTP", async () => {
    const user = userEvent.setup();
    verifyDeviceMock.mockReturnValue(true);
    enableTwoFactorMock.mockReturnValueOnce({ success: true, verified: false });
    const onClose = jest.fn();
    const reload = jest.spyOn(router, "reload");
    const { container } = render(
      <TestApp
        me={{ features: [{ code: "two_factor" }], hasTwoFactorEnabled: false }}
      >
        <EnableTwoFactorDialog open onClose={onClose} />
      </TestApp>,
    );
    expect(enableTwoFactorMock).not.toHaveBeenCalled();

    await user.click(await screen.findByText("Enable", { selector: "button" }));

    expect(enableTwoFactorMock).toHaveBeenCalled();
    expect(reload).not.toHaveBeenCalled();

    await user.type(screen.getByTestId("token-input"), "111111");
    await user.click(screen.getByText("Confirm"));
    expect(verifyDeviceMock).toHaveBeenCalledWith("111111");
  });

  it("does nothing on click on 'cancel'", async () => {
    const user = userEvent.setup();
    const onClose = jest.fn();
    const { container } = render(
      <TestApp
        me={{ features: [{ code: "two_factor" }], hasTwoFactorEnabled: false }}
      >
        <EnableTwoFactorDialog open onClose={onClose} />
      </TestApp>,
    );
    expect(enableTwoFactorMock).not.toHaveBeenCalled();

    await user.click(await screen.findByText("Cancel", { selector: "button" }));

    expect(enableTwoFactorMock).not.toHaveBeenCalled();
    expect(onClose).toHaveBeenCalled();
  });
});

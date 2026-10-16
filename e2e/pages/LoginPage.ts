import { Locator, Page, expect } from "@playwright/test";

export class LoginPage {
  constructor(private readonly page: Page) {}

  get emailInput() {
    return this.page.getByTestId("email");
  }

  get passwordInput() {
    return this.page.getByTestId("password");
  }

  get submitButton() {
    return this.page.getByTestId("submit");
  }

  get errorMessage() {
    return this.page.getByTestId("error");
  }

  async goto() {
    await this.page.goto("/login/");
    await expect(
      this.page.getByRole("heading", { name: "Sign in" }),
    ).toBeVisible();
  }

  async login(email: string, password: string) {
    await this.emailInput.fill(email);
    await this.passwordInput.fill(password);
    await this.submitButton.click();
  }

  // --- two-factor ----------------------------------------------------------

  /** Shown instead of the credentials once an account with 2FA has entered them. */
  get otpPrompt(): Locator {
    return this.page.getByText(
      "Enter the OTP code you received in your mailbox.",
    );
  }

  get otpInput(): Locator {
    return this.page.getByTestId("token");
  }

  /** Types the emailed code and finishes signing in. */
  async submitOtp(code: string) {
    await this.otpInput.fill(code);
    await this.submitButton.click();
    await expect(this.page).not.toHaveURL(/\/login/);
  }

  get signUpLink() {
    return this.page.getByRole("link", { name: "Sign up" });
  }

  /** Self sign-up asks only for an address; the rest comes by email. */
  get signUpHeading() {
    return this.page.getByRole("heading", { name: "Sign up" });
  }

  get forgotPasswordLink() {
    return this.page.getByRole("link", { name: "Forgot your password?" });
  }

  /** The reset page answers the same whether or not the account exists. */
  async requestPasswordReset(email: string) {
    await this.forgotPasswordLink.click();
    await expect(
      this.page.getByRole("heading", { name: "Password reset" }),
    ).toBeVisible();
    await this.page.getByRole("textbox", { name: "Email address" }).fill(email);
    await this.page.getByRole("button", { name: "Reset" }).click();
    await expect(
      this.page.getByRole("heading", { name: "Password reset sent" }),
    ).toBeVisible();
  }
}

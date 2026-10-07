import { Page, expect } from "@playwright/test";

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

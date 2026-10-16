import { Locator, Page, expect } from "@playwright/test";

/** /auth/reset/<uid>/<token>/, reached from the link in a password reset email. */
export class ResetPasswordPage {
  constructor(private readonly page: Page) {}

  get heading(): Locator {
    return this.page.getByRole("heading", { name: "Set a new password" });
  }

  get doneHeading(): Locator {
    return this.page.getByRole("heading", { name: "Password changed!" });
  }

  async open(link: URL) {
    await this.page.goto(link.href);
    await expect(this.heading).toBeVisible();
  }

  /** Both fields are labelled "Password", so they go by name. */
  async setPassword(password: string) {
    await this.page.locator('input[name="password1"]').fill(password);
    await this.page.locator('input[name="password2"]').fill(password);
    await this.page.getByRole("button", { name: "Set password" }).click();
    await expect(this.doneHeading).toBeVisible();
  }
}

import { Locator, Page, expect } from "@playwright/test";

/**
 * /register, reached from the link in an invitation or sign-up email. Without
 * both the `email` and `token` query params it bounces to the login page.
 */
export class RegisterPage {
  constructor(private readonly page: Page) {}

  get heading(): Locator {
    return this.page.getByRole("heading", { name: "Create your account" });
  }

  /** Read-only: the address the invitation was sent to. */
  get emailInput(): Locator {
    return this.page.getByRole("textbox", { name: "Email address" });
  }

  get submitButton(): Locator {
    return this.page.getByTestId("submit");
  }

  /** Opens the emailed link and waits for the form. */
  async open(link: URL) {
    await this.page.goto(link.href);
    await expect(this.heading).toBeVisible();
  }

  /** Both password fields are labelled the same way, so they go by name. */
  async register(firstName: string, lastName: string, password: string) {
    await this.page.getByRole("textbox", { name: "First name" }).fill(firstName);
    await this.page.getByRole("textbox", { name: "Last name" }).fill(lastName);
    await this.page.locator('input[name="password1"]').fill(password);
    await this.page.locator('input[name="password2"]').fill(password);
    await this.submitButton.click();
    await this.page.waitForURL((url) => !url.pathname.startsWith("/register"));
  }
}

import { Locator, Page, expect } from "@playwright/test";

export const ACCOUNT_PATH = "/user/account/";

/** /user/account: profile, security, access tokens and invitations. */
export class AccountSettingsPage {
  constructor(private readonly page: Page) {}

  async goto() {
    await this.page.goto(ACCOUNT_PATH);
    await expect(this.heading).toBeVisible();
  }

  get heading(): Locator {
    return this.headingIn("Your account");
  }

  /**
   * The page title, as the interface's language renders it. The layout draws it
   * as plain text next to the Logout button, not as a heading.
   */
  headingIn(text: string): Locator {
    return this.page.getByText(text).first();
  }

  /** The profile and security sections lay out <dt>/<dd> pairs. */
  private value(term: string): Locator {
    return this.page
      .getByRole("term")
      .filter({ hasText: term })
      .locator("xpath=following-sibling::dd");
  }

  // --- profile -------------------------------------------------------------

  get editButton(): Locator {
    return this.page.getByRole("button", { name: "Edit", exact: true });
  }

  get saveButton(): Locator {
    return this.page.getByRole("button", { name: "Save", exact: true });
  }

  field(term: "First name" | "Last name" | "Email" | "Joined"): Locator {
    return this.value(term);
  }

  input(term: "First name" | "Last name"): Locator {
    return this.value(term).getByRole("textbox");
  }

  /** The profile section is titled with the display name. */
  sectionTitle(displayName: string): Locator {
    return this.page.getByRole("heading", { name: displayName, level: 4 });
  }

  async readName(): Promise<{ firstName: string; lastName: string }> {
    return {
      firstName: (await this.field("First name").innerText()).trim(),
      lastName: (await this.field("Last name").innerText()).trim(),
    };
  }

  async setName(firstName: string, lastName: string) {
    await this.editButton.click();
    await this.input("First name").fill(firstName);
    await this.input("Last name").fill(lastName);
    await this.saveButton.click();
    await expect(this.saveButton).toBeHidden();
    await expect(this.field("First name")).toHaveText(firstName);
  }

  // --- security ------------------------------------------------------------

  get twoFactorStatus(): Locator {
    return this.value("Two-Factor Authentication");
  }

  get enableTwoFactorButton(): Locator {
    return this.twoFactorStatus.getByRole("button", { name: "Enable" });
  }

  get enableTwoFactorDialog(): Locator {
    return this.page.getByRole("dialog").filter({
      has: this.page.getByRole("heading", {
        name: "Enable Two-Factor Authentication",
      }),
    });
  }

  // --- access tokens -------------------------------------------------------

  /** A workspace's row, by the workspace's name. */
  tokenRow(workspaceName: string): Locator {
    return this.page
      .getByRole("row")
      .filter({ has: this.page.getByText(workspaceName, { exact: true }) });
  }

  tokenRole(workspaceName: string): Locator {
    return this.tokenRow(workspaceName).getByRole("cell").nth(1);
  }

  showTokenButton(workspaceName: string): Locator {
    return this.tokenRow(workspaceName).getByRole("button", {
      name: "Show the access token",
    });
  }

  hideTokenButton(workspaceName: string): Locator {
    return this.tokenRow(workspaceName).getByRole("button", {
      name: "Hide the access token",
    });
  }

  revealedToken(workspaceName: string): Locator {
    return this.tokenRow(workspaceName).locator("code");
  }

  maskedToken(workspaceName: string): Locator {
    return this.tokenRow(workspaceName).getByText("*********", { exact: true });
  }
}

import { Locator, Page, expect } from "@playwright/test";

import { workspacePaths } from "../config/environment";

export type WebappType = "iFrame" | "Static";

export class WorkspaceWebappsPage {
  constructor(private readonly page: Page) {}

  /**
   * The create form lays its fields out as <dt>/<dd> pairs and leaves the
   * controls without accessible names, so each one is reached through its term.
   */
  private field(term: string): Locator {
    return this.page
      .getByRole("term")
      .filter({ hasText: term })
      .locator("xpath=following-sibling::dd");
  }

  get nameInput(): Locator {
    return this.field("Name").getByRole("textbox");
  }

  get sourceUrlInput(): Locator {
    return this.field("Source URL").getByRole("textbox");
  }

  get typeSelect(): Locator {
    return this.field("Type").getByRole("combobox");
  }

  get submitButton(): Locator {
    return this.page.getByRole("button", { name: "Create", exact: true });
  }

  get deleteButton(): Locator {
    return this.page.getByRole("button", { name: "Delete", exact: true });
  }

  get deleteDialog(): Locator {
    return this.page.getByRole("dialog").filter({
      has: this.page.getByRole("heading", { name: "Delete web app" }),
    });
  }

  row(name: string): Locator {
    return this.page
      .getByRole("row")
      .filter({ has: this.page.getByText(name, { exact: true }) });
  }

  async goto() {
    await this.page.goto(workspacePaths.webapps);
  }

  /** Creates a web app and waits for the redirect to it. Returns its slug. */
  async create(type: WebappType, name: string): Promise<string> {
    await this.page.goto(`${workspacePaths.webapps}create/`);

    await this.nameInput.fill(name);
    await this.typeSelect.selectOption(type);
    if (type === "iFrame") {
      await this.sourceUrlInput.fill("https://example.com/");
    }
    // A Static app starts from a prefilled HTML template, so it needs no source.

    await this.submitButton.click();
    // The create page itself sits at .../webapps/create/, so matching a single
    // trailing segment is not enough to tell that the redirect has happened.
    await this.page.waitForURL(
      (url) =>
        /\/webapps\/[^/]+\/?$/.test(url.pathname) &&
        !url.pathname.includes("/create"),
    );

    return this.page.url().replace(/\/$/, "").split("/webapps/")[1];
  }

  async gotoWebapp(slug: string) {
    await this.page.goto(`${workspacePaths.webapps}${slug}/`);
  }

  async delete() {
    await this.deleteButton.click();
    await this.deleteDialog.getByRole("button", { name: "Delete" }).click();
    await this.page.waitForURL(`**${workspacePaths.webapps}`);
  }

  async deleteIfPresent(slug: string) {
    const response = await this.page.goto(`${workspacePaths.webapps}${slug}/`);
    if (response?.status() === 404) {
      return;
    }
    await this.delete();
  }

  async expectVisible(name: string) {
    await this.goto();
    await expect(this.row(name)).toBeVisible();
  }
}

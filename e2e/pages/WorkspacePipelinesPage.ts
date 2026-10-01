import { Locator, Page, expect } from "@playwright/test";

import { workspacePaths } from "../config/environment";

export class WorkspacePipelinesPage {
  constructor(private readonly page: Page) {}

  get templatesTable(): Locator {
    return this.page.getByRole("tabpanel", { name: "Available Templates" });
  }

  get deleteButton(): Locator {
    return this.page.getByRole("button", { name: "Delete", exact: true });
  }

  get deleteDialog(): Locator {
    return this.page.getByRole("dialog").filter({
      has: this.page.getByRole("heading", { name: "Delete pipeline" }),
    });
  }

  row(name: string): Locator {
    return this.page
      .getByRole("row")
      .filter({ has: this.page.getByRole("link", { name, exact: true }) });
  }

  async goto() {
    await this.page.goto(workspacePaths.pipelines);
  }

  async gotoTemplates() {
    await this.page.goto(`${workspacePaths.pipelines}?tab=templates`);
    await expect(
      this.templatesTable
        .getByRole("button", { name: "Create pipeline" })
        .first(),
    ).toBeVisible();
  }

  /**
   * Builds a pipeline from the first template on offer. The catalogue is shared
   * demo data, so the test takes whatever is listed first rather than naming a
   * template that may be renamed or unpublished.
   */
  async createFromFirstTemplate(): Promise<{ name: string; code: string }> {
    await this.gotoTemplates();

    const firstRow = this.templatesTable.getByRole("row").nth(1);
    const name = (await firstRow.getByRole("link").first().innerText()).trim();

    await firstRow.getByRole("button", { name: "Create pipeline" }).click();
    await this.page.waitForURL(
      (url) =>
        /\/pipelines\/[^/]+\/?$/.test(url.pathname) &&
        !url.search.includes("tab="),
    );

    const code = this.page.url().replace(/\/$/, "").split("/pipelines/")[1];
    return { name, code };
  }

  async gotoPipeline(code: string) {
    await this.page.goto(`${workspacePaths.pipelines}${code}/`);
  }

  async delete() {
    await this.deleteButton.click();
    await this.deleteDialog.getByRole("button", { name: "Delete" }).click();
    await this.page.waitForURL(`**${workspacePaths.pipelines}`);
  }

  async deleteIfPresent(code: string) {
    const response = await this.page.goto(
      `${workspacePaths.pipelines}${code}/`,
    );
    if (response?.status() === 404) {
      return;
    }
    await this.delete();
  }
}

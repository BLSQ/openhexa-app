import { Locator, Page, expect } from "@playwright/test";

import { workspacePaths } from "../config/environment";

const templatesPath = workspacePaths.home.replace(/\/$/, "/templates/");

/**
 * Publishing a pipeline as a template, and the template's own pages. A
 * published template is offered to every user of the platform, so tests
 * delete theirs again in cleanup.
 */
export class WorkspaceTemplatesPage {
  constructor(private readonly page: Page) {}

  get publishButton(): Locator {
    return this.page.getByRole("button", { name: "Publish as Template" });
  }

  get publishDialog(): Locator {
    return this.page.getByRole("dialog");
  }

  private toast(text: string | RegExp): Locator {
    return this.page.getByText(text);
  }

  /** The description is a rich-text editor without a name of its own. */
  private async typeInEditor(field: Locator, text: string) {
    await field.locator("[contenteditable=true]").click();
    await this.page.keyboard.type(text);
  }

  private fieldOf(label: string): Locator {
    return this.publishDialog
      .getByText(label, { exact: true })
      .locator("xpath=ancestor::div[2]");
  }

  /**
   * Publishes the pipeline open on the page as a new template, and returns
   * the template's code from the page publishing redirects to.
   */
  async publishNew(name: string, description: string): Promise<string> {
    await this.publishButton.click();
    await this.publishDialog.getByLabel("Template name").fill(name);
    await this.typeInEditor(this.fieldOf("Template description"), description);
    await this.publishDialog.getByLabel(/I confirm that I want to publish/).check();
    await this.publishDialog
      .getByRole("button", { name: "Create a new Template" })
      .click();
    await expect(
      this.toast(`New Template '${name}' created successfully.`),
    ).toBeVisible();
    await this.page.waitForURL(/\/templates\/[^/]+\/?$/);
    return this.page.url().replace(/\/$/, "").split("/templates/")[1];
  }

  /** Publishes the pipeline open on the page as the template's next version. */
  async publishVersion(templateName: string, changelog: string) {
    // A pipeline that already has a template offers this instead.
    await this.page
      .getByRole("button", { name: "Publish a new Template Version" })
      .click();
    await this.publishDialog.getByLabel("Changelog").fill(changelog);
    await this.publishDialog.getByLabel(/I confirm that I want to publish/).check();
    await this.publishDialog
      .getByRole("button", {
        name: `Add a new version to Template '${templateName}'`,
      })
      .click();
    await expect(
      this.toast(`New Template Version for '${templateName}' created successfully.`),
    ).toBeVisible();
  }

  async gotoTemplate(code: string, tab: "" | "code/" | "versions/" = "") {
    return this.page.goto(`${templatesPath}${code}/${tab}`);
  }

  get heading(): Locator {
    return this.page.getByRole("heading", { level: 2 });
  }

  /** Deletion asks for the template's name to be typed back. */
  async delete(name: string) {
    await this.page.getByRole("button", { name: "Delete", exact: true }).click();
    const dialog = this.page.getByRole("dialog").filter({
      has: this.page.getByRole("heading", { name: "Delete template" }),
    });
    await dialog.getByPlaceholder(name).fill(name);
    await dialog.getByRole("button", { name: "Delete" }).click();
    await expect(this.toast(`Successfully deleted template ${name}`)).toBeVisible();
  }

  async deleteIfPresent(code: string, name: string) {
    const response = await this.gotoTemplate(code);
    if (response?.status() === 404) {
      return;
    }
    await this.delete(name);
  }

  // --- the pipelines page's Templates tab ----------------------------------

  get catalogue(): Locator {
    return this.page.getByRole("tabpanel", { name: "Available Templates" });
  }

  catalogueRow(name: string): Locator {
    return this.catalogue
      .getByRole("row")
      .filter({ has: this.page.getByRole("link", { name, exact: true }) });
  }

  async searchCatalogue(name: string) {
    await this.page.goto(`${workspacePaths.pipelines}?tab=templates`);
    await this.catalogue.getByRole("textbox").first().fill(name);
    await expect(this.catalogueRow(name)).toBeVisible();
  }

  /** Builds a pipeline from a template in the catalogue. Returns its code. */
  async createPipelineFrom(name: string): Promise<string> {
    await this.searchCatalogue(name);
    await this.catalogueRow(name)
      .getByRole("button", { name: "Create pipeline" })
      .click();
    await this.page.waitForURL(
      (url) =>
        /\/pipelines\/[^/]+\/?$/.test(url.pathname) &&
        !url.search.includes("tab="),
    );
    return this.page.url().replace(/\/$/, "").split("/pipelines/")[1];
  }

  // --- a pipeline built from a template ------------------------------------

  async upgradePipeline() {
    await this.page.getByRole("button", { name: "Upgrade to latest version" }).click();
    await this.page
      .getByRole("dialog")
      .getByRole("button", { name: "Upgrade", exact: true })
      .click();
    await expect(this.toast("Pipeline upgraded successfully")).toBeVisible();
  }
}

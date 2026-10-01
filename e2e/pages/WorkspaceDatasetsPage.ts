import { Locator, Page, expect } from "@playwright/test";

import { workspace, workspacePaths } from "../config/environment";
import { acceptNextConfirm } from "../helpers/confirm";

export class WorkspaceDatasetsPage {
  constructor(private readonly page: Page) {}

  private dialog(heading: string): Locator {
    return this.page
      .getByRole("dialog")
      .filter({ has: this.page.getByRole("heading", { name: heading }) });
  }

  get createButton(): Locator {
    return this.page.getByRole("button", { name: "Create", exact: true });
  }

  get createDialog(): Locator {
    return this.dialog("Create a dataset");
  }

  get newVersionButton(): Locator {
    return this.page.getByRole("button", { name: "Create new version" });
  }

  get newVersionDialog(): Locator {
    return this.dialog("Upload a new version");
  }

  /** Deletes the dataset itself; confirms with `window.confirm`. */
  get deleteDatasetButton(): Locator {
    return this.page.getByRole("button", { name: "Delete", exact: true });
  }

  get deleteVersionButton(): Locator {
    return this.page.getByRole("button", { name: "Delete version" });
  }

  get deleteVersionDialog(): Locator {
    return this.dialog("Delete Version");
  }

  row(name: string): Locator {
    return this.page
      .getByRole("row")
      .filter({ has: this.page.getByRole("link", { name, exact: true }) });
  }

  async goto() {
    await this.page.goto(workspacePaths.datasets);
    await expect(
      this.page.getByRole("columnheader", { name: "Name" }),
    ).toBeVisible();
  }

  /** Creates a dataset and waits for the redirect to it. Returns its slug. */
  async create(name: string, description: string): Promise<string> {
    await this.createButton.click();
    await this.createDialog.getByRole("textbox", { name: "Name" }).fill(name);
    await this.createDialog
      .getByRole("textbox", { name: "Description" })
      .fill(description);
    await this.createDialog.getByRole("button", { name: "Create" }).click();

    await this.page.waitForURL(/\/datasets\/[^/]+\/from\/[^/]+\/?$/);
    return this.page.url().split("/datasets/")[1].split("/")[0];
  }

  /** A version needs both a name and at least one file; the dialog rejects either alone. */
  async createVersion(versionName: string, fileName: string) {
    await this.newVersionButton.click();
    await this.newVersionDialog
      .getByRole("tab", { name: "Upload files" })
      .click();
    await this.newVersionDialog
      .getByRole("textbox", { name: "Name" })
      .fill(versionName);
    await this.newVersionDialog
      .locator('input[type="file"]:not([webkitdirectory])')
      .setInputFiles({
        name: fileName,
        mimeType: "text/csv",
        buffer: Buffer.from("id,value\n1,ok\n"),
      });
    await this.newVersionDialog.getByRole("button", { name: "Create" }).click();

    await expect(this.newVersionDialog).toBeHidden();
    await expect(this.deleteVersionButton).toBeVisible();
  }

  async deleteVersion() {
    await this.deleteVersionButton.click();
    await this.deleteVersionDialog
      .getByRole("button", { name: "Delete Version" })
      .click();
    await expect(this.deleteVersionDialog).toBeHidden();
  }

  async deleteDataset() {
    acceptNextConfirm(this.page);
    await this.deleteDatasetButton.click();
    await this.page.waitForURL(`**${workspacePaths.datasets}`);
  }

  /** Asking for the dataset is decisive where a row count in the list is not. */
  async deleteIfPresent(slug: string) {
    const response = await this.page.goto(
      `${workspacePaths.datasets}${slug}/from/${workspace.slug}/`,
    );
    if (response?.status() === 404) {
      return;
    }
    await this.deleteDataset();
  }
}

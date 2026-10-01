import { Locator, Page, expect } from "@playwright/test";

import { workspacePaths } from "../config/environment";
import { acceptNextConfirm } from "../helpers/confirm";
import { waitForGrid } from "../helpers/grid";

export class WorkspaceFilesPage {
  constructor(private readonly page: Page) {}

  get createFolderButton(): Locator {
    return this.page.getByRole("button", { name: "Create a folder" });
  }

  get uploadButton(): Locator {
    return this.page.getByRole("button", { name: "Upload files" });
  }

  private dialog(heading: string): Locator {
    return this.page
      .getByRole("dialog")
      .filter({ has: this.page.getByRole("heading", { name: heading }) });
  }

  get createFolderDialog(): Locator {
    return this.dialog("Create a folder");
  }

  get uploadDialog(): Locator {
    return this.dialog("Upload files in workspace");
  }

  row(name: string): Locator {
    return this.page
      .getByRole("row")
      .filter({ has: this.page.getByText(name, { exact: true }) });
  }

  async goto() {
    await this.page.goto(workspacePaths.files);
    await expect(
      this.page.getByRole("columnheader", { name: "Name" }),
    ).toBeVisible();
  }

  /** Creating a folder navigates into it, so this returns to the files root. */
  async createFolder(name: string) {
    await this.createFolderButton.click();
    await this.createFolderDialog
      .getByRole("textbox", { name: "Folder name" })
      .fill(name);
    await this.createFolderDialog
      .getByRole("button", { name: "Create" })
      .click();
    await this.page.waitForURL(
      `**${workspacePaths.files}${encodeURIComponent(name)}/`,
    );
    await this.goto();
  }

  async uploadFile(name: string, contents: string) {
    await this.uploadButton.click();
    // The dialog has a second, directory-picking input next to this one.
    await this.uploadDialog
      .locator('input[type="file"]:not([webkitdirectory])')
      .setInputFiles({
        name,
        mimeType: "text/csv",
        buffer: Buffer.from(contents),
      });
    await this.uploadDialog.getByRole("button", { name: "Upload" }).click();
    await expect(this.uploadDialog).toBeHidden();
  }

  async delete(name: string) {
    acceptNextConfirm(this.page);
    await this.row(name).getByRole("button", { name: "Delete" }).click();
    await expect(this.row(name)).toHaveCount(0);
  }

  async deleteIfPresent(name: string) {
    await this.goto();
    await waitForGrid(this.page);
    if ((await this.row(name).count()) === 0) {
      return;
    }
    await this.delete(name);
  }
}

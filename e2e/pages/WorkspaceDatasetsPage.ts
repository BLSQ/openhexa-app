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
  async createVersion(
    versionName: string,
    fileName: string,
    contents = "id,value\n1,ok\n",
  ) {
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
        buffer: Buffer.from(contents),
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

  // --- a dataset's pages -----------------------------------------------------

  async gotoDataset(slug: string, workspaceSlug = workspace.slug) {
    await this.page.goto(
      `/workspaces/${workspaceSlug}/datasets/${slug}/from/${workspace.slug}/`,
    );
  }

  /** The dataset's own tabs: General, Files and Access management. */
  async openTab(tab: "General" | "Files" | "Access management") {
    await this.page
      .getByRole("main")
      .getByRole("link", { name: tab, exact: true })
      .click();
  }

  /** The <dt>/<dd> pairs of the General tab and a file's details. */
  field(term: string): Locator {
    return this.page
      .getByRole("main")
      .getByRole("term")
      .filter({ hasText: new RegExp(`^${term}$`) })
      .locator("xpath=following-sibling::dd")
      .first();
  }

  async edit(name: string, description: string) {
    await this.page.getByRole("button", { name: "Edit" }).first().click();
    await this.field("Name").getByRole("textbox").fill(name);
    const editor = this.field("Description").getByRole("textbox", {
      name: "editable markdown",
    });
    await editor.click();
    await this.page.keyboard.press("ControlOrMeta+A");
    await this.page.keyboard.type(description);
    await this.page.getByRole("button", { name: "Save", exact: true }).click();
    await expect(
      this.page.getByRole("button", { name: "Save", exact: true }),
    ).toBeHidden();
  }

  /** The picker in the heading is labelled "<version> - <date>". */
  get versionPicker(): Locator {
    return this.page
      .getByRole("heading", { level: 2 })
      .getByRole("button", { name: / - / });
  }

  async pickVersion(version: string) {
    await this.versionPicker.click();
    await this.page
      .getByRole("option", { name: new RegExp(`^${version} - `) })
      .click();
    await expect(this.versionPicker).toHaveText(new RegExp(`^${version} - `));
  }

  /** The Files tab's preview of the selected file. */
  get previewTable(): Locator {
    return this.page.getByRole("tabpanel", { name: "Preview" }).getByRole("table");
  }

  /** The Columns tab's statistics for one column, under its heading. */
  columnStatistics(column: string): Locator {
    return this.page
      .getByRole("tabpanel", { name: "Columns" })
      .getByRole("heading", { name: column, level: 3 })
      .locator("xpath=following-sibling::*[1]");
  }

  get fileDownloadButton(): Locator {
    return this.page.getByRole("button", { name: "Download", exact: true });
  }

  // --- access --------------------------------------------------------------

  get organizationShareSwitch(): Locator {
    return this.page.getByRole("switch", {
      name: "Share with the whole Organization",
    });
  }

  async setSharedWithOrganization(shared: boolean) {
    if ((await this.organizationShareSwitch.getAttribute("aria-checked")) !== String(shared)) {
      await this.organizationShareSwitch.click();
    }
    await expect(this.organizationShareSwitch).toHaveAttribute(
      "aria-checked",
      String(shared),
    );
  }

  linkRow(workspaceName: string): Locator {
    return this.page
      .getByRole("row")
      .filter({ has: this.page.getByRole("cell", { name: workspaceName, exact: true }) });
  }

  async shareWithWorkspace(workspaceName: string) {
    await this.page.getByRole("button", { name: "Share with a workspace" }).click();
    const dialog = this.page.getByRole("dialog");
    await dialog.getByRole("combobox", { name: "Select a workspace" }).fill(workspaceName);
    await this.page.getByRole("option", { name: workspaceName, exact: true }).click();
    await dialog.getByRole("button", { name: "Link" }).click();
    await expect(dialog).toBeHidden();
    await expect(this.linkRow(workspaceName)).toBeVisible();
  }

  async revokeLink(workspaceName: string) {
    acceptNextConfirm(this.page);
    await this.linkRow(workspaceName).getByRole("button", { name: "Revoke" }).click();
    await expect(this.linkRow(workspaceName)).toHaveCount(0);
  }
}

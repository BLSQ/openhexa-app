import { Locator, Page, expect } from "@playwright/test";

import { workspace } from "../config/environment";
import { acceptNextConfirm } from "../helpers/confirm";
import { dialogTitled } from "../helpers/dialog";
import { graphql } from "../helpers/graphql";
import { waitForGrid } from "../helpers/grid";
import { toast } from "../helpers/toast";

/** The files of the test workspace, or of the workspace with the given slug. */
export class WorkspaceFilesPage {
  constructor(
    private readonly page: Page,
    private readonly workspaceSlug: string = workspace.slug,
  ) {}

  private get path() {
    return `/workspaces/${this.workspaceSlug}/files/`;
  }

  get createFolderButton(): Locator {
    return this.page.getByRole("button", { name: "Create a folder" });
  }

  get uploadButton(): Locator {
    return this.page.getByRole("button", { name: "Upload files" });
  }

  get createFolderDialog(): Locator {
    return dialogTitled(this.page, "Create a folder");
  }

  get uploadDialog(): Locator {
    return dialogTitled(this.page, "Upload files in workspace");
  }

  row(name: string): Locator {
    return this.page
      .getByRole("row")
      .filter({ has: this.page.getByText(name, { exact: true }) });
  }

  async goto() {
    await this.page.goto(this.path);
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
      `**${this.path}${encodeURIComponent(name)}/`,
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
    // The dialog stays open for the transfer itself, which for a file of a few
    // megabytes, sharing the uplink with the other workers, outlasts the default.
    await expect(this.uploadDialog).toBeHidden({ timeout: 90_000 });
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

  // --- browsing --------------------------------------------------------------

  get searchInput(): Locator {
    return this.page.getByRole("main").getByRole("textbox", { name: "Search..." });
  }

  breadcrumb(name: string): Locator {
    return this.page
      .getByRole("navigation", { name: "Breadcrumbs" })
      .getByRole("link", { name, exact: true });
  }

  async openFolder(name: string) {
    // By the text in it: the "public" folder's link also holds its status icon,
    // whose label is part of the link's name.
    await this.row(name)
      .getByRole("link")
      .filter({ has: this.page.getByText(name, { exact: true }) })
      .click();
    await this.page.waitForURL(`**/${encodeURIComponent(name)}/`);
    await expect(this.breadcrumb(name)).toBeVisible();
  }

  /** The search only runs once submitted, and looks through every folder. */
  async search(text: string) {
    await this.searchInput.fill(text);
    await this.searchInput.press("Enter");
    await this.page.waitForURL(new RegExp(`[?&]q=${encodeURIComponent(text)}`));
  }

  async download(name: string) {
    const [download] = await Promise.all([
      this.page.waitForEvent("download"),
      this.row(name).getByRole("button", { name: "Download" }).click(),
    ]);
    return download;
  }

  /** Uploads a local directory through the dialog's folder picker. */
  async uploadDirectory(path: string) {
    await this.uploadButton.click();
    await this.uploadDialog
      .locator("input[type=file][webkitdirectory]")
      .setInputFiles(path);
    await this.uploadDialog.getByRole("button", { name: "Upload" }).click();
    await expect(this.uploadDialog).toBeHidden();
  }

  // --- public files ----------------------------------------------------------

  /**
   * Whether the instance offers public files at all, which is its operator's
   * choice. The page must be on the app.
   */
  async publicFilesOffered(): Promise<boolean> {
    const data = await graphql<{ workspace: { publicFiles: object | null } }>(
      this.page,
      `query ($slug: String!) { workspace(slug: $slug) { publicFiles { url } } }`,
      { slug: this.workspaceSlug },
    );
    return data.workspace.publicFiles !== null;
  }

  /** Stands in for the "public" folder at the root while it does not exist. */
  get publicFolderPlaceholder(): Locator {
    return this.page.getByRole("row").filter({
      has: this.page.getByRole("button", { name: "Create folder", exact: true }),
    });
  }

  /** Creates the "public" folder from its placeholder, which opens it. */
  async createPublicFolder() {
    await this.publicFolderPlaceholder
      .getByRole("button", { name: "Create folder", exact: true })
      .click();
    await this.page.waitForURL(`**${this.path}public/`);
    await expect(this.breadcrumb("public")).toBeVisible();
  }

  /** The icon after the "public" folder's name; it leads admins to the settings. */
  publicFolderStatus(status: "Shared publicly" | "Not shared publicly"): Locator {
    return this.row("public").getByLabel(status, { exact: true });
  }

  copyPublicLinkButton(name: string): Locator {
    return this.row(name).getByRole("button", { name: "Copy public link" });
  }

  /**
   * A file's public link, as its row hands it out. The context needs the
   * clipboard permissions for the page to write it and the test to read it.
   */
  async copyPublicLink(name: string): Promise<string> {
    await this.page
      .context()
      .grantPermissions(["clipboard-read", "clipboard-write"]);
    await this.copyPublicLinkButton(name).click();
    await expect(
      toast(this.page, "Public link copied to the clipboard"),
    ).toBeVisible();
    return this.page.evaluate(() => navigator.clipboard.readText());
  }
}

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

  /** The list's "Access" column. */
  rowAccess(name: string, access: "Public" | "Private"): Locator {
    return this.row(name).getByText(access, { exact: true });
  }

  /** Rendered but hidden while the app has no icon. */
  rowIcon(name: string): Locator {
    return this.row(name).getByRole("img", { name: "Icon" });
  }

  // --- tabs ----------------------------------------------------------------

  tab(name: WebappTab): Locator {
    return this.page.getByRole("link", { name, exact: true });
  }

  async gotoTab(slug: string, tab: WebappTab) {
    return this.page.goto(`${workspacePaths.webapps}${slug}/${TAB_PATHS[tab]}`);
  }

  private toast(text: string): Locator {
    return this.page.getByText(text, { exact: true });
  }

  // --- general -------------------------------------------------------------

  get editButton(): Locator {
    return this.page.getByRole("button", { name: "Edit", exact: true });
  }

  get saveButton(): Locator {
    return this.page.getByRole("button", { name: "Save", exact: true });
  }

  /** The served address, built from the subdomain. */
  get publishedUrl(): Locator {
    return this.field("Published URL").getByRole("link");
  }

  get subdomainInput(): Locator {
    return this.field("Published URL").getByRole("textbox");
  }

  get publicAccessSwitch(): Locator {
    return this.field("Public access").getByRole("switch");
  }

  /** Visually hidden behind its "Change Icon" label. */
  get iconInput(): Locator {
    return this.page.locator("input#file-upload");
  }

  async servedUrl(slug: string): Promise<string> {
    await this.gotoTab(slug, "General");
    return (await this.publishedUrl.getAttribute("href"))!;
  }

  async updateDetails(changes: {
    name?: string;
    sourceUrl?: string;
    subdomain?: string;
    isPublic?: boolean;
    icon?: Buffer;
  }) {
    await this.editButton.click();
    if (changes.name !== undefined) {
      await this.nameInput.fill(changes.name);
    }
    if (changes.sourceUrl !== undefined) {
      await this.sourceUrlInput.fill(changes.sourceUrl);
    }
    if (changes.subdomain !== undefined) {
      await this.subdomainInput.fill(changes.subdomain);
    }
    if (changes.icon !== undefined) {
      await this.iconInput.setInputFiles({
        name: "icon.png",
        mimeType: "image/png",
        buffer: changes.icon,
      });
    }
    if (changes.isPublic !== undefined) {
      await this.publicAccessSwitch.setChecked(changes.isPublic);
    }
    await this.saveButton.click();
    await expect(this.toast("Web app updated successfully")).toBeVisible();
  }

  // --- play ----------------------------------------------------------------

  /** The full-page view of an app, framed. */
  async gotoPlay(slug: string) {
    await this.page.goto(`${workspacePaths.webapps}${slug}/play/`);
  }

  get playFrame(): Locator {
    return this.page.getByTestId("webapp-iframe");
  }

  // --- code ----------------------------------------------------------------

  /** CodeMirror's content area, showing index.html. */
  get codeEditor(): Locator {
    return this.page.locator(".cm-content");
  }

  get publishButton(): Locator {
    return this.page.getByRole("button", { name: "Publish", exact: true });
  }

  /** Replaces index.html. Saving commits and publishes in one go. */
  async editCode(slug: string, html: string) {
    await this.gotoTab(slug, "Code");
    // Filling before the file has loaded would be overwritten when it arrives.
    await expect(this.codeEditor).toContainText("</html>");
    await this.codeEditor.fill(html);
    await this.saveButton.click();
    await expect(this.toast("Web app saved successfully")).toBeVisible();
  }

  /** Opens the code at an older commit and publishes it. */
  async publishVersion(slug: string, commitId: string) {
    await this.page.goto(
      `${workspacePaths.webapps}${slug}/code/?ref=${commitId}`,
    );
    await this.publishButton.click();
    await expect(this.toast("Version published successfully")).toBeVisible();
  }

  // --- history -------------------------------------------------------------

  /** A commit's message links to its diff. */
  commitLink(message: string): Locator {
    return this.page.getByRole("link", { name: message, exact: true });
  }

  /** The line holding a commit's message and, if published, its badge. */
  commitTitle(message: string): Locator {
    return this.commitLink(message).locator("xpath=..");
  }

  async commitId(message: string): Promise<string> {
    const href = await this.commitLink(message).getAttribute("href");
    return href!.replace(/\/$/, "").split("/commits/")[1];
  }

  /** A line of the commit page's diff. */
  diffLine(text: string): Locator {
    return this.page.getByText(text).first();
  }

  get backToHistory(): Locator {
    return this.page.getByRole("link", { name: "← Back to history" });
  }

  // --- API access ----------------------------------------------------------

  apiScope(label: ApiScope): Locator {
    return this.page.getByRole("switch", { name: label });
  }

  async enableApiScope(slug: string, label: ApiScope) {
    await this.gotoTab(slug, "API access");
    await this.editButton.click();
    await this.apiScope(label).setChecked(true);
    await this.saveButton.click();
    await expect(this.toast("API access updated successfully")).toBeVisible();
  }
}

export type WebappTab = "General" | "Code" | "History" | "API access";

const TAB_PATHS: Record<WebappTab, string> = {
  General: "",
  Code: "code/",
  History: "history/",
  "API access": "api-access/",
};

export type ApiScope =
  | "Read datasets"
  | "Read pipelines"
  | "Run pipelines"
  | "Read files"
  | "Read database"
  | "Read user info";

/** A 1x1 PNG, enough for the icon to be resized and stored. */
export const ICON_PNG = Buffer.from(
  "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==",
  "base64",
);

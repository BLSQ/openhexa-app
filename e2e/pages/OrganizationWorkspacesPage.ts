import { Locator, Page, expect } from "@playwright/test";

import { organizationPaths } from "../config/environment";

/** Provisioning a workspace takes far longer than an ordinary page load. */
const PROVISIONING_TIMEOUT = 90_000;

export class OrganizationWorkspacesPage {
  constructor(private readonly page: Page) {}

  get createButton(): Locator {
    return this.page.getByRole("button", { name: "Create Workspace" });
  }

  get searchInput(): Locator {
    return this.page.getByPlaceholder("Search workspaces...");
  }

  get createDialog(): Locator {
    return this.page.getByRole("dialog").filter({
      has: this.page.getByRole("heading", { name: "Create a workspace" }),
    });
  }

  get nameInput(): Locator {
    return this.createDialog.getByRole("textbox", { name: "Workspace name" });
  }

  get submitCreateButton(): Locator {
    return this.createDialog.getByRole("button", {
      name: "Create",
      exact: true,
    });
  }

  archiveDialog(name: string): Locator {
    return this.page.getByRole("dialog").filter({
      has: this.page.getByRole("heading", { name: `Archive ${name}` }),
    });
  }

  row(name: string): Locator {
    return this.page.getByRole("row").filter({
      has: this.page.getByRole("link", { name, exact: true }),
    });
  }

  async goto() {
    await this.page.goto(organizationPaths.workspaces);
  }

  /** The card view hides the per-row actions, so the table view is the one to drive. */
  async showList() {
    await this.page.getByTestId("grid-view").click();
    await expect(
      this.page.getByRole("columnheader", { name: "Name" }),
    ).toBeVisible();
  }

  /**
   * Creates a workspace and waits for the redirect to it. Returns the slug the
   * backend assigned, which is derived from the name but not guaranteed to be.
   */
  async create(name: string): Promise<string> {
    await this.goto();
    await expect(
      this.createButton,
      "the organization has reached its workspace limit",
    ).toBeEnabled();
    await this.createButton.click();

    await this.nameInput.fill(name);
    await this.submitCreateButton.click();

    await this.page.waitForURL(/\/workspaces\/[^/]+\/?$/, {
      timeout: PROVISIONING_TIMEOUT,
    });
    const slug = new URL(this.page.url()).pathname.split("/")[2];
    return slug;
  }

  async archive(name: string) {
    await this.goto();
    await this.showList();
    await this.searchInput.fill(name);

    const row = this.row(name);
    await expect(row).toBeVisible();
    await row.getByRole("button", { name: "Archive" }).click();

    const dialog = this.archiveDialog(name);
    await dialog.getByPlaceholder(name).fill(name);
    await dialog.getByRole("button", { name: "Archive" }).click();

    await expect(row).toHaveCount(0);
  }

  /**
   * Archives a workspace known only by its name, if it turns up within
   * `timeout`. For a creation that timed out before reporting its slug: the
   * backend may still be provisioning it, so it is given time to appear.
   */
  async archiveIfCreated(name: string, timeout = 60_000) {
    await this.goto();
    await this.showList();
    await this.searchInput.fill(name);
    try {
      await expect(async () => {
        await this.page.reload();
        await this.showList();
        await this.searchInput.fill(name);
        await expect(this.row(name)).toBeVisible({ timeout: 5_000 });
      }).toPass({ timeout });
    } catch {
      return;
    }
    await this.archive(name);
  }
}

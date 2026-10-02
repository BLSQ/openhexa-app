import { Page, test as base } from "@playwright/test";
import { randomBytes } from "node:crypto";

import { OrganizationWorkspacesPage } from "../pages/OrganizationWorkspacesPage";

/**
 * A workspace that lives for the duration of one test.
 *
 * The lifecycle test archives it itself, because archiving is part of what it
 * checks. This exists for the run that fails in between: a red test must still
 * leave the shared environment as it found it.
 */
export class DisposableWorkspace {
  readonly name: string;
  private slug: string | null = null;
  private requested = false;

  constructor(private readonly page: Page) {
    const stamp = new Date().toISOString().slice(0, 10).replace(/-/g, "");
    this.name = `E2E temp ${stamp} ${randomBytes(4).toString("hex")}`;
  }

  private get workspaces() {
    return new OrganizationWorkspacesPage(this.page);
  }

  async create(): Promise<string> {
    this.requested = true;
    this.slug = await this.workspaces.create(this.name);
    return this.slug;
  }

  async archive() {
    await this.workspaces.archive(this.name);
  }

  async cleanup() {
    if (!this.slug) {
      // The creation timed out before redirecting, but may still have gone
      // through: the name is unique, so look for it by that.
      if (this.requested) {
        await this.workspaces.archiveIfCreated(this.name);
      }
      return;
    }
    // Asking for the workspace itself is decisive in a way the organization
    // list is not: the list shows its empty state while it loads, so reading a
    // row count there races the fetch.
    const response = await this.page.goto(`/workspaces/${this.slug}/`);
    if (response?.status() === 404) {
      return;
    }
    await this.archive();
  }
}

export const test = base.extend<{ disposableWorkspace: DisposableWorkspace }>({
  disposableWorkspace: async ({ page }, use) => {
    const workspace = new DisposableWorkspace(page);
    await use(workspace);
    await workspace.cleanup();
  },
});

export { expect } from "@playwright/test";

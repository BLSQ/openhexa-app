import { Locator, Page, expect } from "@playwright/test";

import { organizationPaths } from "../config/environment";

/** Every dataset in the organization, with who it is shared with. */
export class OrganizationDatasetsPage {
  constructor(private readonly page: Page) {}

  get searchInput(): Locator {
    return this.page.getByPlaceholder("Search datasets...");
  }

  /** A dataset's row; its link reads "<name> (<slug>)". */
  row(name: string): Locator {
    return this.page
      .getByRole("row")
      .filter({ has: this.page.getByRole("link", { name: `${name} (` }) });
  }

  async goto() {
    await this.page.goto(organizationPaths.datasets);
  }

  async search(name: string) {
    await this.searchInput.fill(name);
    await expect(this.row(name)).toBeVisible();
  }
}

import { Locator, Page, expect } from "@playwright/test";

import { workspacePaths } from "../config/environment";
import { acceptNextConfirm } from "../helpers/confirm";

const databasePath = workspacePaths.home.replace(/\/$/, "/databases/");

/** The workspace database: its table list and one table's rows. */
export class WorkspaceDatabasePage {
  constructor(private readonly page: Page) {}

  get tablesHeading(): Locator {
    return this.page.getByRole("heading", { name: "Tables", level: 2 });
  }

  /** A table's row in the list, which links to the table by its name. */
  tableRow(name: string): Locator {
    return this.page
      .getByRole("row")
      .filter({ has: this.page.getByRole("link", { name, exact: true }) });
  }

  /** The list's "# Rows" cell, e.g. "3 rows". */
  rowCount(name: string): Locator {
    return this.tableRow(name).getByRole("cell").nth(1);
  }

  /** A column header on a table's page reads "<name> <type>". */
  columnHeader(name: string): Locator {
    return this.page.getByRole("columnheader", {
      name: new RegExp(`^${name} `),
    });
  }

  /** The rows of a table's sample, header excluded. */
  get sampleRows(): Locator {
    return this.page.getByRole("main").getByRole("rowgroup").nth(1).getByRole("row");
  }

  get deleteButton(): Locator {
    return this.page.getByRole("button", { name: "Delete", exact: true });
  }

  async goto() {
    await this.page.goto(databasePath);
    await expect(this.tablesHeading).toBeVisible();
  }

  async gotoTable(name: string) {
    return this.page.goto(`${databasePath}${name}/`);
  }

  /** Deleting confirms with `window.confirm`, then returns to the list. */
  async deleteTable(name: string) {
    await this.gotoTable(name);
    acceptNextConfirm(this.page);
    await this.deleteButton.click();
    await this.page.waitForURL(`**${databasePath}`);
    await expect(this.tableRow(name)).toHaveCount(0);
  }

  async deleteTableIfPresent(name: string) {
    const response = await this.gotoTable(name);
    if (response?.status() === 404) {
      return;
    }
    await this.deleteTable(name);
  }
}

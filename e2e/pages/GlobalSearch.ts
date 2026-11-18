import { Locator, Page, expect } from "@playwright/test";

export type SearchTab =
  | "All results"
  | "Datasets"
  | "Tables"
  | "Files"
  | "Pipelines"
  | "Templates";

/** The search opened from the header's "Search..." button, or Ctrl+K. */
export class GlobalSearch {
  constructor(private readonly page: Page) {}

  get openButton(): Locator {
    return this.page.getByRole("button", { name: "Search..." });
  }

  get input(): Locator {
    return this.page.getByPlaceholder(
      "Search for files, pipelines, templates, database, datasets,...",
    );
  }

  /** Each tab is labelled with its result count, e.g. "Tables (1)". */
  tab(name: SearchTab): Locator {
    return this.page.getByRole("tab", { name: new RegExp(`^${name} \\(\\d+\\)$`) });
  }

  resultLink(name: string): Locator {
    return this.page
      .getByRole("tabpanel")
      .getByRole("link", { name, exact: true });
  }

  async search(text: string) {
    await this.openButton.click();
    await expect(this.input).toBeVisible();
    await this.input.fill(text);
  }
}

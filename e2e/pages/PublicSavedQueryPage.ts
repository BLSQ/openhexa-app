import { Locator, Page } from "@playwright/test";

/** A public saved query's permalink, as anyone holding the link sees it. */
export class PublicSavedQueryPage {
  constructor(private readonly page: Page) {}

  static path(slug: string) {
    return `/queries/${slug}`;
  }

  async goto(slug: string) {
    return this.page.goto(PublicSavedQueryPage.path(slug));
  }

  heading(name: string): Locator {
    return this.page.getByRole("heading", { name, level: 1 });
  }

  text(text: string): Locator {
    return this.page.getByText(text);
  }

  /** The footer reads "<n> rows · <ms> ms" once the query has run. */
  get resultSummary(): Locator {
    return this.page.getByText(/^\d+ rows? · [\d,]+ ms$/);
  }

  /** A result row, by the text of one of its cells. */
  resultRow(cell: string): Locator {
    return this.page
      .getByRole("table")
      .getByRole("row")
      .filter({ has: this.page.getByRole("cell", { name: cell, exact: true }) });
  }

  get exportCsvButton(): Locator {
    return this.page.getByRole("button", { name: "Export CSV" });
  }

  /** Only offered to visitors who are not signed in. */
  get loginLink(): Locator {
    return this.page.getByRole("link", { name: "Log in" });
  }

  /** Only offered to members of the query's workspace. */
  get openInDataStudioLink(): Locator {
    return this.page.getByRole("link", { name: "Open in Data Studio" });
  }

  /**
   * Exports the full result and returns the file's content. The page posts a
   * form into a hidden frame, so the download is the frame's.
   */
  async exportCsv(): Promise<string> {
    const downloading = this.page.waitForEvent("download");
    await this.exportCsvButton.click();
    const stream = await (await downloading).createReadStream();
    const chunks: Buffer[] = [];
    for await (const chunk of stream) {
      chunks.push(chunk as Buffer);
    }
    return Buffer.concat(chunks).toString("utf8");
  }
}

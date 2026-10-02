import { Locator, Page, expect } from "@playwright/test";

import { workspacePaths } from "../config/environment";

export type Sharing = "Private" | "Workspace";

export class WorkspaceDataStudioPage {
  constructor(private readonly page: Page) {}

  private dialog(heading: string): Locator {
    return this.page.getByRole("dialog").filter({
      has: this.page.getByRole("heading", { name: heading }),
    });
  }

  async goto() {
    await this.page.goto(workspacePaths.dataStudio);
    await expect(this.sqlEditor).toBeVisible();
  }

  // --- editor --------------------------------------------------------------

  /** CodeMirror's content area. Filling it replaces the whole query. */
  get sqlEditor(): Locator {
    return this.page.locator(".cm-content");
  }

  get runButton(): Locator {
    return this.page.getByRole("button", { name: "Run", exact: true });
  }

  get maxRows(): Locator {
    // The wrapping <label> lends the select its name, followed by the option.
    return this.page.getByRole("combobox", { name: /^Max rows/ });
  }

  /** Replaces the query and runs it, waiting for the result to come back. */
  async run(sql: string) {
    await this.sqlEditor.fill(sql);
    await this.runButton.click();
    await expect(
      this.page.getByRole("button", { name: "Running…" }),
    ).toBeHidden();
  }

  // --- results -------------------------------------------------------------

  get resultsTable(): Locator {
    return this.page.getByRole("table");
  }

  /** The footer reads "Query OK" and then "<n> rows · <ms> ms". */
  get resultSummary(): Locator {
    return this.page.getByText(/^\d+ rows? · [\d,]+ ms$/);
  }

  /** The cells of a result row; the first one is the row number. */
  resultCells(row: number | "last"): Locator {
    const rows = this.resultsTable.getByRole("row");
    return (row === "last" ? rows.last() : rows.nth(row)).getByRole("cell");
  }

  get queryError(): Locator {
    return this.page.getByText("The query could not be executed.");
  }

  /** The database's own message, printed under the summary. */
  queryErrorDetail(text: string): Locator {
    return this.page.locator("pre").filter({ hasText: text });
  }

  /** Only rendered when the columns follow a widget convention. */
  get resultTabs(): Locator {
    return this.page.getByRole("tablist");
  }

  resultTab(name: "Chart" | "Map" | "Table"): Locator {
    return this.resultTabs.getByRole("tab", { name, exact: true });
  }

  /** A bar chart is drawn with divs: a row is its label, its bar and its value. */
  bar(label: string): Locator {
    return this.page.getByTitle(label, { exact: true }).locator("xpath=..");
  }

  get lineChart(): Locator {
    return this.page.getByRole("img", { name: "Line chart" });
  }

  /** The y ticks are vertically centred on their gridline; the x labels are not. */
  get lineXLabels(): Locator {
    return this.lineChart.locator("text:not([dominant-baseline])");
  }

  get pieChart(): Locator {
    return this.page.getByRole("img", { name: "Pie chart" });
  }

  get pieSlices(): Locator {
    return this.pieChart.locator("path");
  }

  /** A pie legend row: label, value and share. */
  pieSlice(label: string): Locator {
    return this.page
      .getByRole("listitem")
      .filter({ has: this.page.getByTitle(label, { exact: true }) });
  }

  get mapCanvas(): Locator {
    return this.page.locator("canvas.maplibregl-canvas");
  }

  /** The feature popup lists the row's other columns as <dt>/<dd> pairs. */
  mapPopupValue(column: string): Locator {
    return this.page
      .locator(".maplibregl-popup")
      .getByRole("term")
      .filter({ hasText: column })
      .locator("xpath=following-sibling::dd");
  }

  /**
   * The map frames the result on load, so its centre lands on whatever feature
   * covers the middle of the result's extent. MapLibre only accepts clicks once
   * it has drawn, which the retry covers.
   */
  async clickMapCentre(expectedPopupColumn: string) {
    await expect(this.mapCanvas).toBeVisible();
    await expect(async () => {
      await this.mapCanvas.click();
      await expect(this.mapPopupValue(expectedPopupColumn)).toBeVisible({
        timeout: 2_000,
      });
    }).toPass({ timeout: 30_000 });
  }

  // --- saved queries: editor -----------------------------------------------

  get saveButton(): Locator {
    return this.page.getByRole("button", { name: "Save", exact: true });
  }

  get editDetailsButton(): Locator {
    return this.page.getByRole("button", { name: "Edit details" });
  }

  get saveDialog(): Locator {
    return this.dialog("Save query");
  }

  get editDetailsDialog(): Locator {
    return this.dialog("Edit details");
  }

  /** The toolbar shows the saved query's name, followed by its slug. */
  queryName(slug: string): Locator {
    return this.page
      .getByText(`(${slug})`, { exact: true })
      .locator("xpath=preceding-sibling::span[1]");
  }

  /** The toolbar's sharing popover, labelled with the current setting. */
  sharingButton(current: Sharing): Locator {
    return this.page.getByRole("button", { name: current, exact: true });
  }

  get makePrivateDialog(): Locator {
    return this.dialog("Make this query private?");
  }

  private async fillDetails(
    dialog: Locator,
    details: { name: string; description: string; sharing: Sharing },
  ) {
    await dialog.getByRole("textbox", { name: "Name" }).fill(details.name);
    // The description's label is not associated with its textarea.
    await dialog
      .getByPlaceholder("What does this query return? Any caveats?")
      .fill(details.description);
    // The radios are visually hidden, so the card that labels each is clicked.
    const radio = dialog.getByRole("radio", {
      name: new RegExp(`^${details.sharing}`),
    });
    await radio.locator("xpath=ancestor::label").click();
    await expect(radio).toBeChecked();
  }

  /** Saves the SQL as a new query and waits for its page. Returns its slug. */
  async create(
    sql: string,
    details: { name: string; description: string; sharing: Sharing },
  ): Promise<string> {
    await this.goto();
    await this.sqlEditor.fill(sql);
    await this.saveButton.click();
    await this.fillDetails(this.saveDialog, details);
    await this.saveDialog.getByRole("button", { name: "Save query" }).click();
    await this.page.waitForURL(/\/data-studio\/queries\/[^/]+\/?$/);
    return this.page.url().replace(/\/$/, "").split("/queries/")[1];
  }

  async gotoQuery(slug: string) {
    return this.page.goto(`${workspacePaths.savedQueries}${slug}/`);
  }

  async editDetails(details: {
    name: string;
    description: string;
    sharing: Sharing;
  }) {
    await this.editDetailsButton.click();
    await this.fillDetails(this.editDetailsDialog, details);
    await this.editDetailsDialog
      .getByRole("button", { name: "Save", exact: true })
      .click();
    await expect(this.editDetailsDialog).toBeHidden();
  }

  /** Saves edits to the SQL in place. Save is disabled again once committed. */
  async saveSql(sql: string) {
    await this.sqlEditor.fill(sql);
    await this.saveButton.click();
    await expect(this.page.getByText("Query saved")).toBeVisible();
    await expect(this.saveButton).toBeDisabled();
  }

  /** Switching back to private asks for confirmation; sharing does not. */
  async makePrivate() {
    await this.sharingButton("Workspace").click();
    await this.page.getByRole("menuitem", { name: /^Private/ }).click();
    await this.makePrivateDialog
      .getByRole("button", { name: "Make private" })
      .click();
    await expect(this.sharingButton("Private")).toBeVisible();
  }

  // --- saved queries: list -------------------------------------------------

  get searchBox(): Locator {
    return this.page.getByPlaceholder("Search saved queries…");
  }

  get deleteDialog(): Locator {
    return this.dialog("Delete saved query");
  }

  /** Rows are not links, so a row is found by the slug printed under its name. */
  row(slug: string): Locator {
    return this.page
      .getByRole("row")
      .filter({ has: this.page.getByText(slug, { exact: true }) });
  }

  /** The list's columns, read off the row in display order. */
  cell(slug: string, column: "Name" | "Description" | "Visibility"): Locator {
    const index = { Name: 0, Description: 1, Visibility: 3 }[column];
    return this.row(slug).getByRole("cell").nth(index);
  }

  /** Opens the list filtered on `search`, which matches names and descriptions. */
  async gotoList(search?: string) {
    await this.page.goto(workspacePaths.savedQueries);
    await expect(
      this.page.getByRole("columnheader", { name: "Name" }),
    ).toBeVisible();
    if (search) {
      await this.searchBox.fill(search);
      await this.page.waitForLoadState("networkidle");
    }
  }

  async deleteFromList(slug: string) {
    await this.row(slug).getByRole("button", { name: "Delete" }).click();
    await this.deleteDialog
      .getByRole("button", { name: "Delete", exact: true })
      .click();
    await expect(this.deleteDialog).toBeHidden();
  }

  /**
   * Deletion lives on the list only, which is searched by name -- and a test
   * that failed partway may have renamed the query, so the current name is read
   * off its page first.
   */
  async deleteIfPresent(slug: string) {
    const response = await this.gotoQuery(slug);
    if (response?.status() === 404) {
      return;
    }
    const name = (await this.queryName(slug).innerText()).trim();
    await this.gotoList(name);
    await this.deleteFromList(slug);
  }
}

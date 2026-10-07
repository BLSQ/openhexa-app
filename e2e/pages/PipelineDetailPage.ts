import { Locator, Page, expect } from "@playwright/test";

import { workspacePaths } from "../config/environment";
import { acceptNextConfirm } from "../helpers/confirm";

export type FunctionalType =
  | "Computation"
  | "Extraction"
  | "Loading"
  | "Transformation";

export type NotificationLevel = "All" | "Error";

/**
 * One pipeline's General, Runs and Scheduling tabs and its versions page.
 * Their cards each have an Edit button and lay out <dt>/<dd> pairs.
 */
export class PipelineDetailPage {
  constructor(
    private readonly page: Page,
    private readonly code: string,
  ) {}

  private path(sub = "") {
    return `${workspacePaths.pipelines}${this.code}/${sub}`;
  }

  async gotoGeneral() {
    await this.page.goto(this.path());
    await this.page.waitForLoadState("networkidle");
  }

  async gotoScheduling() {
    await this.page.goto(this.path("notifications/"));
    await this.page.waitForLoadState("networkidle");
  }

  async gotoRuns() {
    await this.page.goto(this.path("runs/"));
  }

  async gotoVersions() {
    await this.page.goto(this.path("versions/"));
  }

  get heading(): Locator {
    return this.page.getByRole("heading", { level: 2 });
  }

  field(term: string): Locator {
    return this.page
      .getByRole("main")
      .getByRole("term")
      .filter({ hasText: new RegExp(`^${term}$`) })
      .locator("xpath=following-sibling::dd");
  }

  /** The cards' Edit buttons, in page order. */
  editButton(index = 0): Locator {
    return this.page.getByRole("button", { name: "Edit", exact: true }).nth(index);
  }

  get saveButton(): Locator {
    return this.page.getByRole("button", { name: "Save", exact: true });
  }

  async save() {
    await this.saveButton.click();
    await expect(this.saveButton).toBeHidden();
  }

  // --- general -------------------------------------------------------------

  /** The Information card's fields; the description is a rich-text editor. */
  async editInformation(values: {
    name: string;
    description: string;
    tag: string;
    type: FunctionalType;
  }) {
    await this.editButton(0).click();
    await this.field("Name").getByRole("textbox").fill(values.name);

    const description = this.field("Description").getByRole("textbox", {
      name: "editable markdown",
    });
    await description.click();
    await this.page.keyboard.type(values.description);

    await this.field("Tags").getByPlaceholder("Add a tag...").fill(values.tag);
    await this.field("Tags").getByRole("button", { name: "Add Tag" }).click();

    await this.field("Type").getByRole("button").click();
    await this.page
      .getByRole("option", { name: values.type, exact: true })
      .click();

    await this.save();
  }

  // --- webhook -------------------------------------------------------------

  /** The Webhook card is the second one with an Edit button. */
  async setWebhookEnabled(enabled: boolean) {
    await this.editButton(1).click();
    const toggle = this.field("Enabled").getByRole("switch");
    if ((await toggle.getAttribute("aria-checked")) !== String(enabled)) {
      await toggle.click();
    }
    await this.save();
  }

  get webhookUrl(): Locator {
    return this.field("URL").locator("code");
  }

  async regenerateWebhookUrl() {
    await this.editButton(1).click();
    await this.page.getByRole("button", { name: "Generate a new URL" }).click();
    await this.page
      .getByRole("dialog")
      .getByRole("button", { name: "Generate", exact: true })
      .click();
    await this.page.getByRole("button", { name: "Cancel" }).click();
  }

  // --- default values ------------------------------------------------------

  get defaultsDialog(): Locator {
    return this.page.getByRole("dialog").filter({
      has: this.page.getByRole("heading", { name: "Set default configuration" }),
    });
  }

  async openDefaults() {
    await this.page.getByRole("button", { name: "Set default values" }).click();
    await expect(this.defaultsDialog).toBeVisible();
  }

  async saveDefaults() {
    await this.defaultsDialog.getByRole("button", { name: "Save" }).click();
    await expect(this.defaultsDialog).toBeHidden();
  }

  /** A row of the General tab's Parameters table, by the parameter's code. */
  parameterRow(code: string): Locator {
    return this.page
      .getByRole("row")
      .filter({ has: this.page.getByRole("cell", { name: code, exact: true }) });
  }

  // --- scheduling ----------------------------------------------------------

  get scheduleInput(): Locator {
    return this.page.getByPlaceholder("0 15 * * *");
  }

  /** Turns the schedule on and types `cron`, without saving. */
  async startScheduling(cron: string) {
    await this.editButton(0).click();
    const toggle = this.field("Enabled").getByRole("switch");
    if ((await toggle.getAttribute("aria-checked")) !== "true") {
      await toggle.click();
    }
    await this.scheduleInput.fill(cron);
  }

  async stopScheduling() {
    await this.editButton(0).click();
    await this.field("Enabled").getByRole("switch").click();
    await this.save();
    await expect(this.field("Enabled").getByRole("switch")).toHaveAttribute(
      "aria-checked",
      "false",
    );
  }

  /** A recipient's row, by the user's display name. */
  recipientRow(displayName: string): Locator {
    return this.page
      .getByRole("row")
      .filter({ has: this.page.getByRole("cell", { name: displayName, exact: true }) });
  }

  /** Adds the first member the picker offers, and returns their name. */
  async addRecipient(level: NotificationLevel): Promise<string> {
    await this.page.getByRole("combobox", { name: "Select member" }).click();
    const option = this.page.getByRole("option").first();
    const name = (await option.innerText()).trim().split("\n")[0];
    await option.click();
    await this.page
      .getByRole("combobox", { name: "Select notification level" })
      .click();
    await this.page.getByRole("option", { name: level, exact: true }).click();
    // The new row's only button is the check that saves it.
    await this.page
      .getByRole("row")
      .filter({ has: this.page.getByRole("combobox", { name: "Select member" }) })
      .getByRole("button")
      .last()
      .click();
    await expect(this.recipientRow(name)).toContainText(level);
    return name;
  }

  /** Its buttons are bare icons: edit, then remove. */
  async removeRecipient(displayName: string) {
    acceptNextConfirm(this.page);
    await this.recipientRow(displayName).getByRole("button").nth(1).click();
    await expect(this.recipientRow(displayName)).toHaveCount(0);
  }

  // --- runs ----------------------------------------------------------------

  /** The Runs tab's rows, header excluded. */
  get runRows(): Locator {
    return this.page.getByRole("main").getByRole("rowgroup").nth(1).getByRole("row");
  }

  // --- versions ------------------------------------------------------------

  /** A version's card on the versions page, by its name, e.g. "v2". */
  versionCard(version: string): Locator {
    return this.page.getByRole("article").filter({
      has: this.page.getByRole("heading", {
        name: new RegExp(`^Version ${version}\\b`),
      }),
    });
  }

  async editVersion(version: string, values: { name: string; description: string }) {
    const card = this.versionCard(version);
    await card.getByRole("button", { name: "Edit" }).click();
    await card
      .getByRole("term")
      .filter({ hasText: "Name" })
      .locator("xpath=following-sibling::dd")
      .getByRole("textbox")
      .fill(values.name);
    await card
      .getByRole("term")
      .filter({ hasText: "Description" })
      .locator("xpath=following-sibling::dd")
      .getByRole("textbox")
      .fill(values.description);
    await card.getByRole("button", { name: "Save" }).click();
    await expect(card.getByRole("button", { name: "Save" })).toBeHidden();
  }

  async deleteVersion(version: string) {
    acceptNextConfirm(this.page);
    await this.versionCard(version).getByRole("button", { name: "Delete" }).click();
    await expect(this.versionCard(version)).toHaveCount(0);
  }
}

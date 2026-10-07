import { Locator, Page, expect } from "@playwright/test";

import { workspacePaths } from "../config/environment";
import { acceptNextConfirm } from "../helpers/confirm";

/** The labels the create dialog shows for each supported integration. */
export const CONNECTION_TYPES = [
  "PostgreSQL",
  "Amazon S3 Bucket",
  "Google GCS Bucket",
  "IASO Account",
  "DHIS2 Instance",
  "Custom",
] as const;

export type ConnectionType = (typeof CONNECTION_TYPES)[number];

/**
 * How to fill each type's required fields. Addressed by visible label, except
 * where the app leaves a control with no accessible name -- GCS's service
 * account key is a Textarea its Field label is not associated with -- which only
 * an attribute selector can reach.
 */
type FieldFill = { value: string } & ({ label: string } | { selector: string });

/**
 * Nothing here points at a real service: these tests only check that a
 * connection round-trips, and never press "Test connection".
 */
const REQUIRED_FIELDS: Record<ConnectionType, FieldFill[]> = {
  PostgreSQL: [
    { label: "Database name", value: "e2e_database" },
    { label: "Host", value: "127.0.0.1" },
    { label: "Username", value: "postgres" },
    { label: "Password", value: "not-a-real-password" },
  ],
  "Amazon S3 Bucket": [{ label: "Bucket name", value: "e2e-bucket" }],
  "Google GCS Bucket": [
    { label: "Bucket name", value: "e2e-bucket" },
    { selector: 'textarea[name="service_account_key"]', value: "{}" },
  ],
  "IASO Account": [
    { label: "Iaso Instance URL", value: "https://iaso.invalid" },
    { label: "Username", value: "e2e" },
    { label: "Password", value: "not-a-real-password" },
  ],
  "DHIS2 Instance": [
    { label: "URL", value: "https://dhis2.invalid" },
    { label: "Username", value: "e2e" },
    { label: "Password", value: "not-a-real-password" },
  ],
  Custom: [],
};

export class WorkspaceConnectionsPage {
  constructor(private readonly page: Page) {}

  /** The header button, which unlike the empty-state one is always present. */
  get createButton(): Locator {
    return this.page.getByRole("button", { name: "Add connection" });
  }

  get dialog(): Locator {
    return this.page.getByRole("dialog");
  }

  /** Connections are listed as cards, each a link wrapping a heading. */
  card(name: string): Locator {
    return this.page.getByRole("link").filter({
      has: this.page.getByRole("heading", { name, exact: true, level: 4 }),
    });
  }

  async goto() {
    await this.page.goto(workspacePaths.connections);
  }

  async gotoConnection(id: string) {
    await this.page.goto(`${workspacePaths.connections}${id}/`);
  }

  /** Creates a connection and waits for the redirect to it. Returns its id. */
  async create(type: ConnectionType, name: string): Promise<string> {
    await this.createButton.click();
    await this.dialog.getByRole("button", { name: type, exact: true }).click();

    await this.dialog
      .getByRole("textbox", { name: "Connection name", exact: true })
      .fill(name);
    await this.dialog
      .getByRole("textbox", { name: "Description", exact: true })
      .fill("Created by the e2e suite.");

    if (type === "Custom") {
      await this.dialog.getByTestId("add-field").click();
      await this.dialog
        .getByRole("textbox", { name: "Field name", exact: true })
        .fill("e2e_field");
      await this.dialog
        .getByRole("textbox", { name: "Field value", exact: true })
        .fill("e2e-value");
    } else {
      for (const field of REQUIRED_FIELDS[type]) {
        const control =
          "label" in field
            ? this.dialog.getByRole("textbox", {
                name: field.label,
                exact: true,
              })
            : this.dialog.locator(field.selector);
        await control.fill(field.value);
      }
    }

    await this.dialog
      .getByRole("button", { name: "Create connection" })
      .click();
    await this.page.waitForURL(/\/connections\/[0-9a-f-]{36}\/?$/);

    return this.page.url().replace(/\/$/, "").split("/connections/")[1];
  }

  /** Deletes the connection whose page is open; confirms with `window.confirm`. */
  async delete() {
    acceptNextConfirm(this.page);
    await this.page
      .getByRole("button", { name: "Delete", exact: true })
      .click();
    await this.page.waitForURL(`**${workspacePaths.connections}`);
  }

  async deleteIfPresent(id: string) {
    const response = await this.page.goto(
      `${workspacePaths.connections}${id}/`,
    );
    if (response?.status() === 404) {
      return;
    }
    await this.delete();
  }

  async expectVisible(name: string) {
    await this.goto();
    await expect(this.card(name)).toBeVisible();
  }

  // --- a connection's page ---------------------------------------------------

  /** A row of the Fields table: the field's code, then its value. */
  fieldValue(code: string): Locator {
    return this.page
      .getByRole("row")
      .filter({ has: this.page.getByRole("cell", { name: code, exact: true }) })
      .getByRole("cell")
      .nth(1);
  }

  get fieldsDialog(): Locator {
    return this.page.getByRole("dialog").filter({
      has: this.page.getByRole("heading", { name: /^Update connection fields for/ }),
    });
  }

  /** The Fields card's Edit button is the second on the page. */
  async editFields(values: Record<string, string>) {
    await this.page.getByRole("button", { name: "Edit", exact: true }).nth(1).click();
    for (const [label, value] of Object.entries(values)) {
      const textbox = this.fieldsDialog.getByRole("textbox", { name: label, exact: true });
      const control = (await textbox.count())
        ? textbox
        : this.fieldsDialog.getByRole("spinbutton", { name: label, exact: true });
      await control.fill(value);
    }
  }

  /** Presses "Test connection" in the open dialog and returns what it says. */
  async testConnection(): Promise<Locator> {
    await this.fieldsDialog.getByRole("button", { name: "Test connection" }).click();
    const result = this.fieldsDialog.getByText(
      /Connection successful!|Connection failed/,
    );
    await expect(result).toBeVisible({ timeout: 60_000 });
    return result;
  }

  async saveFields() {
    await this.fieldsDialog.getByRole("button", { name: "Save" }).click();
    await expect(this.fieldsDialog).toBeHidden();
  }

  async cancelFields() {
    await this.fieldsDialog.getByRole("button", { name: "Cancel" }).click();
    await expect(this.fieldsDialog).toBeHidden();
  }
}

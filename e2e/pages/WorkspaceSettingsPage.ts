import { Locator, Page, expect } from "@playwright/test";

import { toast } from "../helpers/toast";

export type WorkspaceRole = "Admin" | "Editor" | "Viewer";

/** A workspace's settings page: its General card, members and database. */
export class WorkspaceSettingsPage {
  constructor(private readonly page: Page) {}

  async goto(workspaceSlug: string) {
    await this.gotoTab(workspaceSlug, "Members");
  }

  async gotoTab(workspaceSlug: string, tab: "General" | "Members" | "Database") {
    await this.page.goto(`/workspaces/${workspaceSlug}/settings/`);
    await this.page.getByRole("tab", { name: tab }).click();
  }

  // --- general -------------------------------------------------------------

  /** The General card lays out <dt>/<dd> pairs. */
  field(term: "Name" | "Countries" | "Image" | "Configuration"): Locator {
    return this.page
      .getByRole("tabpanel", { name: "General" })
      .getByRole("term")
      .filter({ hasText: term })
      .locator("xpath=following-sibling::dd");
  }

  get editButton(): Locator {
    return this.page.getByRole("button", { name: "Edit", exact: true });
  }

  get saveButton(): Locator {
    return this.page.getByRole("button", { name: "Save", exact: true });
  }

  async addCountry(country: string) {
    await this.field("Countries")
      .getByRole("combobox", { name: "Select a country" })
      .fill(country);
    await this.page.getByRole("option", { name: country }).first().click();
    // The picker stays open for more choices, over the fields below it.
    await this.page.keyboard.press("Escape");
    await expect(this.page.getByRole("option", { name: country })).toHaveCount(0);
  }

  async addConfiguration(name: string, value: string) {
    await this.page
      .getByRole("tabpanel", { name: "General" })
      .getByRole("button", { name: "Add Configuration" })
      .click();
    const dialog = this.page.getByRole("dialog").filter({
      has: this.page.getByRole("heading", { name: "Add Configuration" }),
    });
    await dialog.getByPlaceholder("Configuration name").fill(name);
    await dialog.getByPlaceholder("Enter value as text or JSON...").fill(value);
    await dialog.getByRole("button", { name: "Add", exact: true }).click();
    await expect(dialog).toBeHidden();
  }

  async save() {
    await this.saveButton.click();
    await expect(this.saveButton).toBeHidden();
  }

  // --- database ------------------------------------------------------------

  /** Regenerates the read-only ("ro") or read & write ("rw") password. */
  async regeneratePassword(access: "ro" | "rw") {
    await this.page
      .getByRole("button", { name: "Regenerate password" })
      .nth(access === "ro" ? 0 : 1)
      .click();
    await this.page
      .getByRole("dialog")
      .filter({
        has: this.page.getByRole("heading", {
          name: "Regenerate database password",
        }),
      })
      .getByRole("button", { name: "Replace password" })
      .click();
    await expect(toast(this.page, "Password successfully changed")).toBeVisible();
  }

  get addMemberButton(): Locator {
    return this.page.getByRole("button", { name: "Add/Invite member" });
  }

  get addMemberDialog(): Locator {
    return this.page.getByRole("dialog").filter({
      has: this.page.getByRole("heading", { name: "Add or invite member" }),
    });
  }

  /**
   * An existing account is added straight away rather than invited; the
   * picker offers it either as a match or as "Invite new user", depending on
   * whether the search can see it, and both end the same way.
   */
  async addMember(email: string, role: WorkspaceRole) {
    await this.addMemberButton.click();
    await this.addMemberDialog.getByPlaceholder("Search users").fill(email);
    await this.page
      .getByRole("option")
      .filter({ hasText: email })
      .first()
      .click();
    // The user picker is a combobox too, so the role select goes by its name.
    await this.addMemberDialog
      .locator('select[name="role"]')
      .selectOption({ label: role });
    // The picker's own button is named after its value, "Invite new user: …".
    await this.addMemberDialog
      .getByRole("button", { name: "Invite", exact: true })
      .click();
    await expect(
      this.page.getByText("Member invited successfully", { exact: true }),
    ).toBeVisible();
  }

  /** A member's row; a pending invitation's row shows the email too, over "Invited by …". */
  memberRow(email: string): Locator {
    return this.page
      .getByRole("row")
      .filter({ has: this.page.getByText(email, { exact: true }) })
      .filter({ hasNot: this.page.getByText(/^Invited by/) });
  }

  // --- invitations ---------------------------------------------------------

  /** A row of the "Pending & Declined invitations" grid, by the invited email. */
  invitationRow(email: string): Locator {
    return this.page
      .getByRole("row")
      .filter({ has: this.page.getByText(email, { exact: true }) })
      .filter({ has: this.page.getByText(/^Invited by/) });
  }

  private invitationDialog(title: string): Locator {
    return this.page.getByRole("dialog").filter({
      has: this.page.getByRole("heading", { name: title }),
    });
  }

  /** The resend and delete buttons are bare icons, in that order. */
  private invitationAction(email: string, action: "resend" | "delete"): Locator {
    return this.invitationRow(email)
      .getByRole("button")
      .nth(action === "resend" ? 0 : 1);
  }

  async resendInvitation(email: string) {
    await this.invitationAction(email, "resend").click();
    await this.invitationDialog("Resend invitation")
      .getByRole("button", { name: "Resend" })
      .click();
    await expect(
      this.page.getByText("Invitation resent", { exact: true }),
    ).toBeVisible();
  }

  async deleteInvitation(email: string) {
    await this.invitationAction(email, "delete").click();
    await this.invitationDialog("Delete invitation")
      .getByRole("button", { name: "Delete" })
      .click();
    await expect(
      this.page.getByText("Invitation deleted", { exact: true }),
    ).toBeVisible();
    await expect(this.invitationRow(email)).toHaveCount(0);
  }

  async deleteInvitationIfPresent(workspaceSlug: string, email: string) {
    await this.goto(workspaceSlug);
    await this.page.waitForLoadState("networkidle");
    if ((await this.invitationRow(email).count()) === 0) {
      return;
    }
    await this.deleteInvitation(email);
  }

  /** The row's role cell, e.g. "Editor". */
  memberRole(email: string): Locator {
    return this.memberRow(email).getByRole("cell").nth(2);
  }

  /** The edit and remove buttons are bare icons, in that order. */
  private memberAction(email: string, action: "edit" | "remove"): Locator {
    return this.memberRow(email)
      .getByRole("button")
      .nth(action === "edit" ? 0 : 1);
  }

  async changeRole(email: string, role: WorkspaceRole) {
    await this.memberAction(email, "edit").click();
    const dialog = this.page.getByRole("dialog").filter({
      has: this.page.getByRole("heading", { name: "Edit member" }),
    });
    await dialog.locator('select[name="role"]').selectOption({ label: role });
    await dialog.getByRole("button", { name: "Save" }).click();
    await expect(
      this.page.getByText("Member role updated successfully", { exact: true }),
    ).toBeVisible();
    await expect(this.memberRole(email)).toHaveText(role);
  }

  async removeMember(email: string) {
    await this.memberAction(email, "remove").click();
    const dialog = this.page.getByRole("dialog").filter({
      has: this.page.getByRole("heading", { name: "Remove member" }),
    });
    await dialog.getByRole("button", { name: "Delete" }).click();
    await expect(
      this.page.getByText("Member removed successfully", { exact: true }),
    ).toBeVisible();
    await expect(this.memberRow(email)).toHaveCount(0);
  }
}

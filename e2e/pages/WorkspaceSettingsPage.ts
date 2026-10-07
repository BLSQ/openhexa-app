import { Locator, Page, expect } from "@playwright/test";

export type WorkspaceRole = "Admin" | "Editor" | "Viewer";

/** A workspace's settings page, as far as its members go. */
export class WorkspaceSettingsPage {
  constructor(private readonly page: Page) {}

  async goto(workspaceSlug: string) {
    await this.page.goto(`/workspaces/${workspaceSlug}/settings/`);
    await this.page.getByRole("tab", { name: "Members" }).click();
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
    await this.addMemberDialog.getByRole("button", { name: "Invite" }).click();
    await expect(
      this.page.getByText("Member invited successfully", { exact: true }),
    ).toBeVisible();
  }

  memberRow(email: string): Locator {
    return this.page
      .getByRole("row")
      .filter({ has: this.page.getByText(email, { exact: true }) });
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

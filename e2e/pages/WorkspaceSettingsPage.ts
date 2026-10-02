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
}

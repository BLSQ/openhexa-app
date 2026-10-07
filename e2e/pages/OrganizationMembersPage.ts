import { Locator, Page, expect } from "@playwright/test";

import { organizationPaths } from "../config/environment";
import { waitForGrid } from "../helpers/grid";
import { OrganizationRole } from "./OrganizationExternalCollaboratorsPage";
import { WorkspaceRole } from "./WorkspaceSettingsPage";

/** The organization's members and its pending invitations. */
export class OrganizationMembersPage {
  constructor(private readonly page: Page) {}

  get searchInput(): Locator {
    return this.page.getByPlaceholder("Search members...");
  }

  get inviteButton(): Locator {
    return this.page.getByRole("button", { name: "Invite member" });
  }

  /** A member's row; the user cell shows the email under the name. */
  row(email: string): Locator {
    return this.page
      .getByRole("row")
      .filter({ has: this.page.getByText(email, { exact: true }) });
  }

  /** The row's "Organization Role" cell. */
  organizationRole(email: string): Locator {
    return this.row(email).getByRole("cell").nth(1);
  }

  workspaceRole(email: string, workspaceName: string, role: WorkspaceRole) {
    return this.row(email).getByText(`${workspaceName} · ${role}`, {
      exact: true,
    });
  }

  /** A pending invitation's row; its first cell holds the email. */
  invitationRow(email: string): Locator {
    return this.page
      .getByRole("row")
      .filter({ has: this.page.getByRole("cell", { name: email }) });
  }

  private dialog(title: string): Locator {
    return this.page.getByRole("dialog").filter({
      has: this.page.getByRole("heading", { name: title }),
    });
  }

  private toast(text: string): Locator {
    return this.page.getByText(text, { exact: true });
  }

  async goto() {
    await this.page.goto(organizationPaths.members);
  }

  async search(email: string) {
    await this.searchInput.fill(email);
    await expect(this.row(email)).toBeVisible();
  }

  async setOrganizationRole(email: string, role: OrganizationRole) {
    await this.row(email).getByRole("button", { name: "edit" }).click();
    const dialog = this.dialog("Update Member Permissions");
    await dialog
      .locator('select[name="organizationRole"]')
      .selectOption({ label: role });
    await dialog.getByRole("button", { name: "Update" }).click();
    await expect(this.toast("Permissions updated!")).toBeVisible();
    await expect(this.organizationRole(email)).toHaveText(role);
  }

  /** Ends their organization membership; their workspace roles stay. */
  async remove(email: string) {
    await this.row(email).getByRole("button", { name: "delete" }).click();
    const dialog = this.dialog("Remove Member");
    await dialog.getByRole("button", { name: "Remove" }).click();
    await expect(this.toast("Member removed")).toBeVisible();
    await expect(this.row(email)).toHaveCount(0);
  }

  async removeIfMember(email: string) {
    await this.goto();
    await this.searchInput.fill(email);
    await waitForGrid(this.page);
    if ((await this.row(email).count()) === 0) {
      return;
    }
    await this.remove(email);
  }

  /** Invites an address with no workspace roles. */
  async invite(email: string, role: OrganizationRole) {
    // The dialog clears its form whenever the page's organization query
    // settles, which wipes an address typed before then.
    await waitForGrid(this.page);
    await this.inviteButton.click();
    const dialog = this.dialog("Invite Member");
    await dialog
      .locator('select[name="organizationRole"]')
      .selectOption({ label: role });
    await dialog.locator("select#bulkRole").selectOption({ label: "None" });
    await dialog.getByPlaceholder("Enter email address").fill(email);
    await dialog.getByRole("button", { name: "Invite Member" }).click();
    await expect(this.toast("Invitation sent!")).toBeVisible();
    await expect(this.invitationRow(email)).toBeVisible();
  }

  /** The resend and delete buttons are bare icons, in that order. */
  private invitationAction(email: string, action: "resend" | "delete") {
    return this.invitationRow(email)
      .getByRole("button")
      .nth(action === "resend" ? 0 : 1);
  }

  async resendInvitation(email: string) {
    await this.invitationAction(email, "resend").click();
    await this.dialog("Resend invitation")
      .getByRole("button", { name: "Resend" })
      .click();
    await expect(this.toast("Invitation resent")).toBeVisible();
  }

  async deleteInvitation(email: string) {
    await this.invitationAction(email, "delete").click();
    await this.dialog("Delete invitation")
      .getByRole("button", { name: "Delete" })
      .click();
    await expect(this.toast("Invitation deleted")).toBeVisible();
    await expect(this.invitationRow(email)).toHaveCount(0);
  }

  async deleteInvitationIfPresent(email: string) {
    await this.goto();
    await waitForGrid(this.page);
    if ((await this.invitationRow(email).count()) === 0) {
      return;
    }
    await this.deleteInvitation(email);
  }
}

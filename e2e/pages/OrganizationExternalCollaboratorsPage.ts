import { Locator, Page, expect } from "@playwright/test";

import { organizationPaths } from "../config/environment";
import { waitForGrid } from "../helpers/grid";
import { toast } from "../helpers/toast";
import { WorkspaceRole } from "./WorkspaceSettingsPage";

export type OrganizationRole = "Owner" | "Admin" | "Member";

/** Workspace users of the organization who are not members of it. */
export class OrganizationExternalCollaboratorsPage {
  constructor(private readonly page: Page) {}

  get searchInput(): Locator {
    return this.page.getByPlaceholder("Search external collaborators...");
  }

  /** The row's user cell shows the email under the name. */
  row(email: string): Locator {
    return this.page
      .getByRole("row")
      .filter({ has: this.page.getByText(email, { exact: true }) });
  }

  /**
   * A row of the page's "Pending Direct Workspace Invitations" grid: an
   * invitation into one workspace, sent to an email without an account.
   */
  pendingInvitationRow(email: string): Locator {
    return this.page
      .getByRole("row")
      .filter({ has: this.page.getByText(email, { exact: true }) })
      .filter({ has: this.page.getByText(/^Invited by/) });
  }

  /** A badge in the row's "Workspace Roles" column. */
  workspaceRole(email: string, workspaceName: string, role: WorkspaceRole) {
    return this.row(email).getByText(`${workspaceName} · ${role}`, {
      exact: true,
    });
  }

  private dialog(title: string): Locator {
    return this.page.getByRole("dialog").filter({
      has: this.page.getByRole("heading", { name: title }),
    });
  }

  private toast(text: string): Locator {
    return toast(this.page, text);
  }

  async goto() {
    await this.page.goto(organizationPaths.externalCollaborators);
  }

  /**
   * Narrows the list to one collaborator, so the row does not depend on
   * which page of the grid they land on.
   */
  async search(email: string) {
    await this.searchInput.fill(email);
    await expect(this.row(email)).toBeVisible();
  }

  /**
   * Narrows the list to someone who may no longer be on it, and waits for the
   * filtered list itself, so that a row or a role missing afterwards is
   * absent rather than not loaded yet or folded behind "+N more".
   */
  async searchSettled(email: string) {
    const filtered = this.page.waitForResponse(
      (response) =>
        response.url().includes("/graphql") &&
        (response.request().postData() ?? "").includes(email),
    );
    await this.searchInput.fill(email);
    await (await filtered).finished();
    await waitForGrid(this.page);
    await this.showAllRoles(email);
  }

  /** Only the first two roles show until the row's "+N more" is clicked. */
  async showAllRoles(email: string) {
    const more = this.row(email).getByRole("button", { name: /^\+\d+ more$/ });
    if (await more.isVisible()) {
      await more.click();
    }
  }

  /** Sets their role in one workspace, by its slug, from the edit dialog. */
  async setWorkspaceRole(
    email: string,
    workspaceSlug: string,
    role: WorkspaceRole | "None",
  ) {
    await this.row(email).getByRole("button", { name: "edit" }).click();
    const dialog = this.dialog("Update Member Permissions");
    await dialog
      .getByRole("radio", {
        name: `${workspaceSlug} ${role.toUpperCase()}`,
        exact: true,
      })
      .check();
    await dialog.getByRole("button", { name: "Update" }).click();
    await expect(this.toast("Permissions updated!")).toBeVisible();
    await expect(dialog).toBeHidden();
  }

  async convertToMember(email: string, role: OrganizationRole) {
    await this.row(email)
      .getByRole("button", { name: "convert to member" })
      .click();
    const dialog = this.dialog("Convert to Organization Member");
    await dialog.locator('select[name="role"]').selectOption({ label: role });
    await dialog.getByRole("button", { name: "Convert to member" }).click();
    await expect(this.toast("Converted to member!")).toBeVisible();
    await expect(this.row(email)).toHaveCount(0);
  }

  /** Takes away every workspace membership they hold in the organization. */
  async remove(email: string) {
    await this.row(email).getByRole("button", { name: "delete" }).click();
    const dialog = this.dialog("Remove External Collaborator");
    await dialog.getByRole("button", { name: "Remove" }).click();
    await expect(this.toast("External collaborator removed")).toBeVisible();
    await expect(this.row(email)).toHaveCount(0);
  }
}

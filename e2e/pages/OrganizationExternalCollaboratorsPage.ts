import { Locator, Page, expect } from "@playwright/test";

import { organizationPaths } from "../config/environment";
import { WorkspaceRole } from "./WorkspaceSettingsPage";

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

  /** A badge in the row's "Workspace Roles" column. */
  workspaceRole(email: string, workspaceName: string, role: WorkspaceRole) {
    return this.row(email).getByText(`${workspaceName} · ${role}`, {
      exact: true,
    });
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

  /** Only the first two roles show until the row's "+N more" is clicked. */
  async showAllRoles(email: string) {
    const more = this.row(email).getByRole("button", { name: /^\+\d+ more$/ });
    if (await more.isVisible()) {
      await more.click();
    }
  }
}

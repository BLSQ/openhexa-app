import { Locator, Page, expect } from "@playwright/test";

import { dialogTitled } from "../helpers/dialog";
import { toast } from "../helpers/toast";

/**
 * The grid of pending invitations, laid out the same on the organization's
 * members page, its external collaborators page and a workspace's settings.
 */
export class PendingInvitations {
  constructor(private readonly page: Page) {}

  /** An invitation's row: its first cell holds the email over "Invited by …". */
  row(email: string): Locator {
    return this.page
      .getByRole("row")
      .filter({ has: this.page.getByText(email, { exact: true }) })
      .filter({ has: this.page.getByText(/^Invited by/) });
  }

  /** The resend and delete buttons are bare icons, in that order. */
  private action(email: string, action: "resend" | "delete"): Locator {
    return this.row(email)
      .getByRole("button")
      .nth(action === "resend" ? 0 : 1);
  }

  async resend(email: string) {
    await this.action(email, "resend").click();
    await dialogTitled(this.page, "Resend invitation")
      .getByRole("button", { name: "Resend" })
      .click();
    await expect(toast(this.page, "Invitation resent")).toBeVisible();
  }

  async delete(email: string) {
    await this.action(email, "delete").click();
    await dialogTitled(this.page, "Delete invitation")
      .getByRole("button", { name: "Delete" })
      .click();
    await expect(toast(this.page, "Invitation deleted")).toBeVisible();
    await expect(this.row(email)).toHaveCount(0);
  }
}

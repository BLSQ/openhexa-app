import { credentials } from "../config/environment";
import { expect, test } from "../fixtures/cleanup";
import { uniqueName } from "../helpers/confirm";
import { OrganizationMembersPage } from "../pages/OrganizationMembersPage";

test.describe("Organization members", () => {
  test("the test account is listed with its role", async ({ page }) => {
    const members = new OrganizationMembersPage(page);

    await members.goto();
    await members.search(credentials.email);
    await expect(members.organizationRole(credentials.email)).toHaveText(
      /Admin|Owner/,
    );
  });

  test("an invitation is sent, resent and deleted", async ({
    page,
    cleanup,
  }) => {
    const members = new OrganizationMembersPage(page);
    // A reserved domain: nothing is delivered, and nobody can accept it.
    const email = `${uniqueName("e2e-invite")}@example.com`;
    cleanup.add(`invitation for ${email}`, () =>
      members.deleteInvitationIfPresent(email),
    );

    await members.goto();
    await members.invite(email, "Member");
    await expect(members.invitationRow(email)).toContainText("Member");

    await members.resendInvitation(email);
    await expect(members.invitationRow(email)).toBeVisible();

    await members.deleteInvitation(email);
    await page.reload();
    await expect(members.invitationRow(email)).toHaveCount(0);
  });
});

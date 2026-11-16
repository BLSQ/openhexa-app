import { BASE_URL, credentials, organization } from "../config/environment";
import { expect, test } from "../fixtures/mailbox";
import { uniqueName } from "../helpers/confirm";
import { linkTo, mailboxAddress } from "../helpers/mailbox";
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
    // A reserved domain: nothing is delivered, and nobody can accept it. The
    // delivered, accepted variant lives in account-lifecycle.spec.ts.
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

  test("an invitation is emailed in the language chosen for it", async ({
    page,
    cleanup,
    mailbox,
  }) => {
    test.setTimeout(180_000);
    const members = new OrganizationMembersPage(page);
    // Never accepted, so that no account is left behind.
    const email = mailboxAddress("e2e-invite-fr");
    cleanup.add(`invitation for ${email}`, () =>
      members.deleteInvitationIfPresent(email),
    );

    const since = new Date();
    await members.goto();
    await members.invite(email, "Member", { language: "Français" });

    // The test account's own language is English: this one is the invitation's.
    const invitation = await mailbox.waitForEmail(email, {
      since,
      subject: `Vous êtes invité(e) à rejoindre l'organisation ${organization.name} sur OpenHEXA`,
    });
    expect(invitation.text).toContain(
      `(${credentials.email}) vous invite à rejoindre l'organisation "${organization.name}" sur OpenHEXA.`,
    );
    const link = linkTo(invitation, "/register");
    expect(link.origin).toBe(new URL(BASE_URL).origin);
    expect(link.searchParams.get("email")).toBe(email);

    await members.deleteInvitation(email);
  });
});

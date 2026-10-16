import { mergeTests } from "@playwright/test";
import { randomBytes } from "node:crypto";

import {
  BASE_URL,
  credentials,
  mailgun,
  organization,
  workspace,
  workspacePaths,
} from "../config/environment";
import { test as mailboxTest } from "../fixtures/mailbox";
import { expect, test as visitorsTest } from "../fixtures/visitors";
import { linkTo, mailboxAddress, otpCode } from "../helpers/mailbox";
import { AccountSettingsPage } from "../pages/AccountSettingsPage";
import { LoginPage } from "../pages/LoginPage";
import { OrganizationMembersPage } from "../pages/OrganizationMembersPage";
import { RegisterPage } from "../pages/RegisterPage";
import { ResetPasswordPage } from "../pages/ResetPasswordPage";
import { WorkspaceSettingsPage } from "../pages/WorkspaceSettingsPage";

const test = mergeTests(visitorsTest, mailboxTest);

/** django-otp refuses to email a second code within a minute of the first. */
const OTP_COOLDOWN = 61_000;

const randomPassword = () => `E2e-${randomBytes(9).toString("base64url")}!`;

/**
 * A throwaway account lives through everything that reaches a user by email:
 * it is invited and registers, is told when it is added to a workspace or the
 * organization, resets its password, and turns two-factor authentication on
 * and off. The account is created by the first test and used by the rest, so
 * they run in order and share it; the shared test account is never touched.
 *
 * Nothing in the app deletes an account, so each run leaves one behind, named
 * `e2e-user-…@` the mailbox domain and a member of nothing. They are purged
 * from the Django admin now and then.
 */
test.describe("Account lifecycle by email", () => {
  test.skip(
    !mailgun,
    "Needs E2E_MAILGUN_API_KEY for a mailbox the suite can read",
  );
  test.describe.configure({ mode: "serial", timeout: 300_000 });

  let email: string;
  let password: string;

  test.beforeAll(() => {
    email = mailboxAddress("e2e-user");
    password = randomPassword();
  });

  test("an organization invitation is emailed, resent, and completes a registration", async ({
    page,
    anonymousPage,
    cleanup,
    mailbox,
  }) => {
    const members = new OrganizationMembersPage(page);
    const register = new RegisterPage(anonymousPage);
    const account = new AccountSettingsPage(anonymousPage);
    cleanup.add(`invitation for ${email}`, () =>
      members.deleteInvitationIfPresent(email),
    );
    cleanup.add(`organization membership of ${email}`, () =>
      members.removeIfMember(email),
    );

    let since = new Date();
    await members.goto();
    await members.invite(email, "Member");

    const first = await mailbox.waitForEmail(email, {
      since,
      subject: `You've been invited to join the organization ${organization.name} on OpenHEXA`,
    });
    // Sent on behalf of whoever invited: the test account.
    expect(first.text).toContain(credentials.email);
    const firstLink = linkTo(first, "/register");
    expect(firstLink.origin).toBe(new URL(BASE_URL).origin);
    expect(firstLink.searchParams.get("email")).toBe(email);
    expect(firstLink.searchParams.get("token")).toBeTruthy();

    await test.step("resending issues a new link", async () => {
      since = new Date();
      await members.resendInvitation(email);
      const second = await mailbox.waitForEmail(email, {
        since,
        subject: first.subject,
      });
      const secondLink = linkTo(second, "/register");
      expect(secondLink.searchParams.get("token")).not.toBe(
        firstLink.searchParams.get("token"),
      );
      await register.open(secondLink);
    });

    await test.step("the link registers the account and signs it in", async () => {
      await expect(register.emailInput).toHaveValue(email);
      await register.register("Playwright", "Invitee", password);
      await account.goto();
      await expect(account.field("Email")).toHaveText(email);
    });

    await test.step("the invitation is accepted", async () => {
      await members.goto();
      await members.search(email);
      await expect(members.organizationRole(email)).toHaveText("Member");
      await expect(members.invitationRow(email)).toHaveCount(0);
    });
  });

  test("inviting the address again adds the existing account at once", async ({
    page,
    cleanup,
    mailbox,
  }) => {
    const members = new OrganizationMembersPage(page);
    cleanup.add(`organization membership of ${email}`, () =>
      members.removeIfMember(email),
    );

    const since = new Date();
    await members.goto();
    await members.invite(email, "Member", { existing: true });
    await expect(members.organizationRole(email)).toHaveText("Member");

    const added = await mailbox.waitForEmail(email, {
      since,
      subject: `You've been added to the organization ${organization.name} on OpenHEXA`,
    });
    expect(added.text).toContain(credentials.email);
    expect(linkTo(added, `/organizations/${organization.id}`)).toBeTruthy();
    expect(added.links.some((link) => link.pathname.startsWith("/register"))).toBe(false);
  });

  test("a member added to a workspace is told by email", async ({
    page,
    anonymousPage,
    cleanup,
    mailbox,
  }) => {
    const settings = new WorkspaceSettingsPage(page);
    const login = new LoginPage(anonymousPage);
    cleanup.add(`workspace membership of ${email}`, async () => {
      await settings.goto(workspace.slug);
      if ((await settings.memberRow(email).count()) > 0) {
        await settings.removeMember(email);
      }
    });

    const since = new Date();
    await settings.goto(workspace.slug);
    await settings.addMember(email, "Viewer");
    await expect(settings.memberRole(email)).toHaveText("Viewer");

    const added = await mailbox.waitForEmail(email, {
      since,
      subject: `You've been added to the workspace ${workspace.name} on OpenHEXA`,
    });
    expect(added.text).toContain(credentials.email);
    const link = linkTo(added, workspacePaths.home.replace(/\/$/, ""));

    await login.goto();
    await login.login(email, password);
    await expect(anonymousPage).not.toHaveURL(/\/login/);
    expect((await anonymousPage.goto(link.href))?.status()).toBe(200);
    await expect(anonymousPage).toHaveURL(new RegExp(workspacePaths.home));
  });

  test("a password reset email sets a new password", async ({
    anonymousPage,
    mailbox,
  }) => {
    const login = new LoginPage(anonymousPage);
    const reset = new ResetPasswordPage(anonymousPage);
    const oldPassword = password;
    const newPassword = randomPassword();

    const since = new Date();
    await login.goto();
    await login.requestPasswordReset(email);

    const mail = await mailbox.waitForEmail(email, {
      since,
      subject: `Password reset on ${new URL(BASE_URL).host}`,
    });
    await reset.open(linkTo(mail, "/auth/reset/"));
    await reset.setPassword(newPassword);
    password = newPassword;

    await login.goto();
    await login.login(email, oldPassword);
    await expect(login.errorMessage).toHaveText(
      "Wrong email address and/or password.",
    );
    await login.login(email, newPassword);
    await expect(anonymousPage).not.toHaveURL(/\/login/);
  });

  test("two-factor authentication is enabled with an emailed code, gates the next sign-in, and is disabled again", async ({
    anonymousPage,
    mailbox,
  }) => {
    const login = new LoginPage(anonymousPage);
    const account = new AccountSettingsPage(anonymousPage);
    const subject = "OpenHEXA Verification Token";
    let lastChallenge = 0;
    const codeSentAfter = async (since: Date) => {
      lastChallenge = Date.now();
      return otpCode(await mailbox.waitForEmail(email, { since, subject }));
    };
    const cooldown = () =>
      new Promise((resolve) =>
        setTimeout(resolve, Math.max(0, lastChallenge + OTP_COOLDOWN - Date.now())),
      );

    await login.goto();
    await login.login(email, password);
    await expect(anonymousPage).not.toHaveURL(/\/login/);

    await test.step("it is enabled with the emailed code", async () => {
      await account.goto();
      await expect(account.twoFactorStatus).toContainText("Currently disabled");
      const since = new Date();
      await account.startEnablingTwoFactor();
      await account.confirmTwoFactorCode(await codeSentAfter(since));
    });

    await test.step("the next sign-in asks for a fresh code", async () => {
      await anonymousPage.context().clearCookies();
      await cooldown();
      const since = new Date();
      await login.goto();
      await login.login(email, password);
      await expect(login.otpPrompt).toBeVisible();
      await login.submitOtp(await codeSentAfter(since));
    });

    await test.step("it is disabled with another code", async () => {
      await account.goto();
      await expect(account.twoFactorStatus).toContainText("Currently enabled");
      await cooldown();
      const since = new Date();
      await account.startDisablingTwoFactor();
      await account.confirmDisableTwoFactorCode(await codeSentAfter(since));
    });
  });

  test("self sign-up sends a verification link", async ({
    anonymousPage,
    mailbox,
  }) => {
    const login = new LoginPage(anonymousPage);
    const register = new RegisterPage(anonymousPage);
    // Its own address: registering it would leave a second account behind,
    // so the link is only opened.
    const address = mailboxAddress("e2e-signup");

    const since = new Date();
    await login.goto();
    await login.signUpLink.click();
    await expect(login.signUpHeading).toBeVisible();
    await anonymousPage
      .getByRole("textbox", { name: "Email address" })
      .fill(address);
    await anonymousPage.getByTestId("submit").click();
    await expect(
      anonymousPage.getByRole("heading", { name: "Check your email" }),
    ).toBeVisible();

    const mail = await mailbox.waitForEmail(address, {
      since,
      subject: "Complete your OpenHEXA registration",
    });
    expect(mail.text).toContain("48 hours");
    const link = linkTo(mail, "/register");
    expect(link.searchParams.get("email")).toBe(address);

    await register.open(link);
    await expect(register.emailInput).toHaveValue(address);
  });
});

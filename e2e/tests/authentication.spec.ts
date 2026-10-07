import { credentials, workspacePaths } from "../config/environment";
import { expect, test } from "../fixtures/visitors";
import { uniqueName } from "../helpers/confirm";
import { LoginPage } from "../pages/LoginPage";
import { UserMenu } from "../pages/UserMenu";

test.describe("Authentication", () => {
  test("a wrong password is refused", async ({ anonymousPage }) => {
    const login = new LoginPage(anonymousPage);

    await login.goto();
    await login.login(credentials.email, "not-the-password");
    await expect(login.errorMessage).toHaveText(
      "Wrong email address and/or password.",
    );
    await expect(anonymousPage).toHaveURL(/\/login/);
  });

  test("a protected page sends a visitor to sign in, and back", async ({
    anonymousPage,
  }) => {
    const login = new LoginPage(anonymousPage);

    await anonymousPage.goto(workspacePaths.files);
    await expect(anonymousPage).toHaveURL(/\/login/);

    await login.login(credentials.email, credentials.password);
    await anonymousPage.waitForURL(`**${workspacePaths.files}`);
  });

  test("signing out ends the session", async ({ anonymousPage }) => {
    const login = new LoginPage(anonymousPage);
    const menu = new UserMenu(anonymousPage, credentials.email);

    // Its own session, so signing out leaves the suite's untouched.
    await login.goto();
    await login.login(credentials.email, credentials.password);
    await expect(anonymousPage).not.toHaveURL(/\/login/);

    await anonymousPage.goto(workspacePaths.home);
    await menu.open();
    await menu.signOutButton.click();
    await expect(anonymousPage).toHaveURL(/\/login/);

    await anonymousPage.goto(workspacePaths.home);
    await expect(anonymousPage).toHaveURL(/\/login/);
  });

  test("a password reset can be requested", async ({ anonymousPage }) => {
    const login = new LoginPage(anonymousPage);

    await login.goto();
    // An address without an account, on a reserved domain: nothing is sent.
    await login.requestPasswordReset(`${uniqueName("e2e-reset")}@example.com`);
  });

  test("sign-up is offered, and registering needs an invitation", async ({
    anonymousPage,
  }) => {
    const login = new LoginPage(anonymousPage);

    await login.goto();
    await login.signUpLink.click();
    await expect(login.signUpHeading).toBeVisible();
    await expect(
      anonymousPage.getByRole("textbox", { name: "Email address" }),
    ).toBeVisible();

    // Registration completes an emailed invitation; without one it bounces.
    await anonymousPage.goto("/register/");
    await expect(anonymousPage).toHaveURL(/\/login/);
  });
});

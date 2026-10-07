import { mergeTests } from "@playwright/test";

import {
  credentials,
  outsiderCredentials,
  workspace,
  workspacePaths,
} from "../config/environment";
import { test as disposableTest } from "../fixtures/disposableWorkspace";
import { expect, test as visitorsTest } from "../fixtures/visitors";
import { uniqueName } from "../helpers/confirm";
import {
  ACCOUNT_PATH,
  AccountSettingsPage,
} from "../pages/AccountSettingsPage";
import { McpPage } from "../pages/McpPage";
import { OrganizationExternalCollaboratorsPage } from "../pages/OrganizationExternalCollaboratorsPage";
import { LABELS, UserMenu } from "../pages/UserMenu";
import { WorkspaceSettingsPage } from "../pages/WorkspaceSettingsPage";

const test = mergeTests(visitorsTest, disposableTest);

const DOCUMENTATION_URL = "https://docs.openhexa.com/#user-manual";

test.describe("User menu", () => {
  test("it leads to account settings, MCP and the documentation", async ({
    page,
  }) => {
    const menu = new UserMenu(page, credentials.email);
    const account = new AccountSettingsPage(page);
    const mcp = new McpPage(page);

    await page.goto(workspacePaths.home);
    await menu.open();
    for (const name of ["Account settings", "MCP", "Documentation"]) {
      await expect(menu.link(name)).toBeVisible();
    }
    await expect(menu.signOutButton).toBeVisible();
    await expect(menu.languageSelect).toHaveValue("en");

    await test.step("Account settings", async () => {
      await menu.link("Account settings").click();
      await page.waitForURL(`**${ACCOUNT_PATH}`);
      await expect(account.heading).toBeVisible();
    });

    await test.step("MCP lists its tools and links to the guide", async () => {
      await page.goto(workspacePaths.home);
      await menu.open();
      await menu.link("MCP").click();
      await expect(mcp.heading).toBeVisible();
      await expect(mcp.summary).toBeVisible();
      await expect(mcp.tool("list_connections")).toBeVisible();
      await expect(mcp.parameterHeadings.first()).toBeVisible();

      await mcp.installLink.click();
      await expect(mcp.guideHeading).toBeVisible();
      await mcp.backToToolsLink.click();
      await expect(mcp.heading).toBeVisible();
    });

    await test.step("Documentation opens the user manual", async () => {
      await page.goto(workspacePaths.home);
      await menu.open();
      await expect(menu.link("Documentation")).toHaveAttribute(
        "href",
        DOCUMENTATION_URL,
      );
      await menu.link("Documentation").click();
      await page.waitForURL(/^https:\/\/docs\.openhexa\.com\//);
    });
  });
});

test.describe("Account settings", () => {
  test("the profile name is changed and changed back", async ({
    page,
    cleanup,
  }) => {
    const account = new AccountSettingsPage(page);
    const menu = new UserMenu(page, credentials.email);
    await account.goto();

    const original = await account.readName();
    cleanup.add("the test account's name", async () => {
      await account.goto();
      const current = await account.readName();
      if (
        current.firstName !== original.firstName ||
        current.lastName !== original.lastName
      ) {
        await account.setName(original.firstName, original.lastName);
      }
    });
    await expect(account.field("Email")).toHaveText(credentials.email);

    const firstName = uniqueName("E2E");
    const lastName = "Renamed";

    await test.step("the new name is shown everywhere", async () => {
      await account.setName(firstName, lastName);

      // The section title only follows the new name after a reload: the save
      // does not send the display name back.
      await account.goto();
      await expect(
        account.sectionTitle(`${firstName} ${lastName}`),
      ).toBeVisible();
      await expect(account.field("First name")).toHaveText(firstName);
      await expect(account.field("Last name")).toHaveText(lastName);

      await page.goto(workspacePaths.home);
      await expect(menu.button).toContainText(`${firstName} ${lastName}`);
    });

    await test.step("the original name comes back", async () => {
      await account.goto();
      await account.setName(original.firstName, original.lastName);
      await account.goto();
      await expect(
        account.sectionTitle(`${original.firstName} ${original.lastName}`),
      ).toBeVisible();
    });
  });

  test("a workspace's access token is shown and hidden", async ({ page }) => {
    const account = new AccountSettingsPage(page);
    await account.goto();

    await expect(account.tokenRole(workspace.name)).toHaveText(
      /^(Admin|Editor)$/,
    );
    await expect(account.maskedToken(workspace.name)).toBeVisible();

    await account.showTokenButton(workspace.name).click();
    await expect(account.revealedToken(workspace.name)).toHaveText(/^\S{20,}$/);
    await expect(account.maskedToken(workspace.name)).toBeHidden();

    await account.hideTokenButton(workspace.name).click();
    await expect(account.maskedToken(workspace.name)).toBeVisible();
    await expect(account.revealedToken(workspace.name)).toBeHidden();
  });

  test("two-factor authentication can be started and cancelled", async ({
    page,
  }) => {
    // Only opened and cancelled: enabling it would lock the shared test account
    // behind a one-time code sent by email.
    const account = new AccountSettingsPage(page);
    await account.goto();
    await expect(account.twoFactorStatus).toContainText("Currently disabled");

    await account.enableTwoFactorButton.click();
    await expect(account.enableTwoFactorDialog).toBeVisible();
    await account.enableTwoFactorDialog
      .getByRole("button", { name: "Cancel" })
      .click();
    await expect(account.enableTwoFactorDialog).toBeHidden();
    await expect(account.twoFactorStatus).toContainText("Currently disabled");
  });
});

test.describe("Seen by another account", () => {
  test.skip(
    !outsiderCredentials,
    "Needs E2E_OUTSIDER_EMAIL / E2E_OUTSIDER_PASSWORD for a second account",
  );
  // The language test changes how the outsider's whole interface reads, so the
  // other test using that account must not run at the same time.
  test.describe.configure({ mode: "serial" });

  test("a member added to a workspace reaches it and gets its token", async ({
    page,
    outsiderPage,
    disposableWorkspace,
  }) => {
    test.setTimeout(240_000);
    const settings = new WorkspaceSettingsPage(page);
    const outsiderAccount = new AccountSettingsPage(outsiderPage);
    const collaborators = new OrganizationExternalCollaboratorsPage(page);
    const email = outsiderCredentials!.email;

    const slug = await disposableWorkspace.create();

    const before = await outsiderPage.goto(`/workspaces/${slug}/`);
    expect(before?.status()).toBe(404);

    await settings.goto(slug);
    await settings.addMember(email, "Editor");

    const after = await outsiderPage.goto(`/workspaces/${slug}/`);
    expect(after?.status()).toBe(200);

    await outsiderAccount.goto();
    await expect(
      outsiderAccount.tokenRole(disposableWorkspace.name),
    ).toHaveText("Editor");

    await test.step(
      "the organization lists them as an external collaborator",
      async () => {
        await collaborators.goto();
        await collaborators.search(email);
        await collaborators.showAllRoles(email);
        await expect(
          collaborators.workspaceRole(email, disposableWorkspace.name, "Editor"),
        ).toBeVisible();
      },
    );
  });

  test("the interface language switches to French and back", async ({
    outsiderPage,
    cleanup,
  }) => {
    const menu = new UserMenu(outsiderPage, outsiderCredentials!.email);
    const account = new AccountSettingsPage(outsiderPage);
    cleanup.add("the outsider's language", () => menu.resetLanguageToEnglish());

    await outsiderPage.goto("/");

    await test.step("French", async () => {
      await menu.switchLanguage("Français");
      await menu.open();
      await expect(menu.languageSelect).toHaveValue("fr");
      await expect(menu.link(LABELS.Français.accountSettings)).toBeVisible();

      await menu.link(LABELS.Français.accountSettings).click();
      await expect(
        account.headingIn(LABELS.Français.yourAccount),
      ).toBeVisible();
    });

    await test.step("back to English", async () => {
      // The account page has no sidebar, so no menu to switch from.
      await outsiderPage.goto("/");
      await menu.switchLanguage("English");
      await menu.open();
      await expect(menu.languageSelect).toHaveValue("en");
      await expect(menu.link(LABELS.English.accountSettings)).toBeVisible();

      await account.goto();
      await expect(account.heading).toBeVisible();
    });
  });
});

import { mergeTests } from "@playwright/test";

import { organizationPaths, outsiderCredentials } from "../config/environment";
import { test as disposableTest } from "../fixtures/disposableWorkspace";
import { expect, test as visitorsTest } from "../fixtures/visitors";
import { AccountSettingsPage } from "../pages/AccountSettingsPage";
import { OrganizationExternalCollaboratorsPage } from "../pages/OrganizationExternalCollaboratorsPage";
import { OrganizationMembersPage } from "../pages/OrganizationMembersPage";
import { OrganizationSidebar } from "../pages/OrganizationSidebar";
import { LABELS, UserMenu } from "../pages/UserMenu";
import { SECTIONS, Section, WorkspaceSections } from "../pages/WorkspaceSections";
import { WorkspaceSettingsPage } from "../pages/WorkspaceSettingsPage";

/**
 * Everything seen through the outsider account: a second user, signed in but
 * with no access to the test workspace until a test grants it some.
 */
const test = mergeTests(visitorsTest, disposableTest);

const ALL_SECTIONS = Object.keys(SECTIONS) as Section[];

test.describe("Seen by another account", () => {
  test.skip(
    !outsiderCredentials,
    "Needs E2E_OUTSIDER_EMAIL / E2E_OUTSIDER_PASSWORD for a second account",
  );
  // These share one account: the language test changes how its whole
  // interface reads, and the others change what it belongs to, so none may
  // run alongside another. "default" runs them one after the other without
  // skipping the rest when one fails.
  test.describe.configure({ mode: "default" });

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

    await test.step("archiving the workspace takes it off the list", async () => {
      await disposableWorkspace.archive();
      await collaborators.goto();
      await collaborators.searchInput.fill(email);
      await expect(
        collaborators.workspaceRole(email, disposableWorkspace.name, "Editor"),
      ).toHaveCount(0);
    });
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

  test("each role sees what it may do, and removal ends access", async ({
    page,
    outsiderPage,
    disposableWorkspace,
  }) => {
    test.setTimeout(300_000);
    const settings = new WorkspaceSettingsPage(page);
    const email = outsiderCredentials!.email;

    const slug = await disposableWorkspace.create();
    const outsider = new WorkspaceSections(outsiderPage, slug);
    const settingsPath = `/workspaces/${slug}/settings/`;

    await settings.goto(slug);
    await settings.addMember(email, "Viewer");

    await test.step("a viewer can look but not add anything", async () => {
      for (const section of ALL_SECTIONS) {
        await outsider.expectCanCreate(section, false);
      }
      await expect(outsider.sidebarLink("JupyterHub")).toHaveCount(0);
      await expect(outsider.sidebarLink("Settings")).toHaveCount(0);
      expect((await outsiderPage.goto(settingsPath))?.status()).toBe(404);
    });

    await test.step("an editor can add, but not manage the workspace", async () => {
      await settings.goto(slug);
      await settings.changeRole(email, "Editor");

      for (const section of ALL_SECTIONS) {
        await outsider.expectCanCreate(section, true);
      }
      await expect(outsider.sidebarLink("JupyterHub")).toBeVisible();
      await expect(outsider.sidebarLink("Settings")).toHaveCount(0);
      expect((await outsiderPage.goto(settingsPath))?.status()).toBe(404);
    });

    await test.step("an admin manages its members", async () => {
      await settings.goto(slug);
      await settings.changeRole(email, "Admin");

      await outsider.goto("Pipelines");
      await expect(outsider.sidebarLink("Settings")).toBeVisible();
      expect((await outsiderPage.goto(settingsPath))?.status()).toBe(200);
      await expect(
        outsiderPage.getByRole("button", { name: "Add/Invite member" }),
      ).toBeHidden();
      await outsiderPage.getByRole("tab", { name: "Members" }).click();
      await expect(
        outsiderPage.getByRole("button", { name: "Add/Invite member" }),
      ).toBeVisible();
    });

    await test.step("a removed member loses the workspace", async () => {
      await settings.goto(slug);
      await settings.removeMember(email);

      const after = await outsiderPage.goto(`/workspaces/${slug}/`);
      expect(after?.status()).toBe(404);
    });
  });

  test("the organization manages an external collaborator's access", async ({
    page,
    outsiderPage,
    disposableWorkspace,
    cleanup,
  }) => {
    test.setTimeout(300_000);
    const settings = new WorkspaceSettingsPage(page);
    const collaborators = new OrganizationExternalCollaboratorsPage(page);
    const members = new OrganizationMembersPage(page);
    const outsiderSidebar = new OrganizationSidebar(outsiderPage);
    const email = outsiderCredentials!.email;
    // Converting them makes the outsider a member of the organization, which
    // the other tests rely on them not being.
    cleanup.add("the outsider's organization membership", () =>
      members.removeIfMember(email),
    );

    const slug = await disposableWorkspace.create();
    const name = disposableWorkspace.name;
    const outsider = new WorkspaceSections(outsiderPage, slug);
    const workspacePath = `/workspaces/${slug}/`;

    await settings.goto(slug);
    await settings.addMember(email, "Editor");

    await test.step("their workspace role is changed from the list", async () => {
      await collaborators.goto();
      await collaborators.search(email);
      await collaborators.setWorkspaceRole(email, slug, "Viewer");
      await collaborators.showAllRoles(email);
      await expect(
        collaborators.workspaceRole(email, name, "Viewer"),
      ).toBeVisible();
      await outsider.expectCanCreate("Pipelines", false);
    });

    await test.step("converted, they are a plain member", async () => {
      await collaborators.convertToMember(email, "Member");

      await members.goto();
      await members.search(email);
      await expect(members.organizationRole(email)).toHaveText("Member");
      await expect(members.workspaceRole(email, name, "Viewer")).toBeVisible();

      await outsiderPage.goto(organizationPaths.workspaces);
      await expect(outsiderSidebar.link("Workspaces")).toBeVisible();
      for (const section of [
        "Members",
        "External Collaborators",
        "Settings",
      ] as const) {
        await expect(outsiderSidebar.link(section)).toHaveCount(0);
      }
    });

    await test.step("made an admin, they manage the organization", async () => {
      await members.setOrganizationRole(email, "Admin");
      await outsiderPage.goto(organizationPaths.workspaces);
      await expect(outsiderSidebar.link("Settings")).toBeVisible();
      await expect(outsiderSidebar.link("Members")).toBeVisible();

      await members.setOrganizationRole(email, "Member");
      await outsiderPage.reload();
      await expect(outsiderSidebar.link("Settings")).toHaveCount(0);
    });

    await test.step("removed from the organization, they lose its workspaces too", async () => {
      await members.remove(email);
      expect((await outsiderPage.goto(workspacePath))?.status()).toBe(404);

      await collaborators.goto();
      await collaborators.searchInput.fill(email);
      await expect(
        collaborators.workspaceRole(email, name, "Viewer"),
      ).toHaveCount(0);
    });

    await test.step("removed as a collaborator, they lose the workspace", async () => {
      await settings.goto(slug);
      await settings.addMember(email, "Editor");

      await collaborators.goto();
      await collaborators.search(email);
      await collaborators.remove(email);
      expect((await outsiderPage.goto(workspacePath))?.status()).toBe(404);
    });
  });
});

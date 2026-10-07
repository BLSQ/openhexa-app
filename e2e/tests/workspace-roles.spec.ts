import { mergeTests } from "@playwright/test";

import { outsiderCredentials } from "../config/environment";
import { test as disposableTest } from "../fixtures/disposableWorkspace";
import { expect, test as visitorsTest } from "../fixtures/visitors";
import { SECTIONS, Section, WorkspaceSections } from "../pages/WorkspaceSections";
import { WorkspaceSettingsPage } from "../pages/WorkspaceSettingsPage";

const test = mergeTests(visitorsTest, disposableTest);

const ALL_SECTIONS = Object.keys(SECTIONS) as Section[];

test.describe("Workspace roles", () => {
  test.skip(
    !outsiderCredentials,
    "Needs E2E_OUTSIDER_EMAIL / E2E_OUTSIDER_PASSWORD for a second account",
  );

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
});

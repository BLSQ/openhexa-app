import { mergeTests } from "@playwright/test";

import { workspace } from "../config/environment";
import { test as cleanupTest } from "../fixtures/cleanup";
import { expect, test as disposableTest } from "../fixtures/disposableWorkspace";
import { uniqueName } from "../helpers/confirm";
import { OrganizationWorkspacesPage } from "../pages/OrganizationWorkspacesPage";

const test = mergeTests(cleanupTest, disposableTest);

// A fixed tag, so repeated runs reuse it rather than leave new ones behind.
const E2E_TAG = "e2e";

test.describe("Organization workspaces", () => {
  test("the list is shown as cards or a table, and searched", async ({
    page,
  }) => {
    const workspaces = new OrganizationWorkspacesPage(page);

    await workspaces.goto();
    await workspaces.showCards();
    await expect(workspaces.card(workspace.name)).toBeVisible();

    await workspaces.showList();
    await expect(workspaces.row(workspace.name)).toBeVisible();

    await workspaces.search(workspace.name);
    await expect(workspaces.row(workspace.name)).toBeVisible();

    await workspaces.search(uniqueName("no such workspace"));
    await expect(workspaces.row(workspace.name)).toHaveCount(0);
  });

  test("a workspace is tagged", async ({ page, disposableWorkspace }) => {
    test.setTimeout(240_000);
    const workspaces = new OrganizationWorkspacesPage(page);

    await disposableWorkspace.create();
    await workspaces.goto();
    await workspaces.showList();
    await workspaces.search(disposableWorkspace.name);

    await workspaces.addTag(disposableWorkspace.name, E2E_TAG);
    await page.reload();
    await workspaces.showList();
    await workspaces.search(disposableWorkspace.name);
    await expect(workspaces.row(disposableWorkspace.name)).toContainText(E2E_TAG);
  });
});

import { organizationPaths } from "../config/environment";
import { expect, test } from "../fixtures/disposableWorkspace";
import { OrganizationWorkspacesPage } from "../pages/OrganizationWorkspacesPage";

// Creating a workspace provisions real resources, so this is the one spec that
// writes to the environment. The disposableWorkspace fixture cleans up after it.
test.describe.configure({ timeout: 150_000 });

test.describe("Workspace lifecycle", () => {
  test("a workspace can be created and archived again", async ({
    page,
    disposableWorkspace,
  }) => {
    const workspaces = new OrganizationWorkspacesPage(page);

    const slug = await disposableWorkspace.create();
    expect(slug).toBeTruthy();
    await expect(page).toHaveTitle(`OpenHEXA | ${disposableWorkspace.name}`);

    await workspaces.goto();
    await workspaces.showList();
    await expect(workspaces.row(disposableWorkspace.name)).toBeVisible();

    // archive() asserts the row disappears from the organization list.
    await disposableWorkspace.archive();

    const response = await page.goto(`/workspaces/${slug}/`);
    expect(response?.status(), "the archived workspace is still served").toBe(
      404,
    );
  });

  test("the create dialog does not submit without a name", async ({ page }) => {
    const workspaces = new OrganizationWorkspacesPage(page);
    await workspaces.goto();

    await workspaces.createButton.click();
    await workspaces.submitCreateButton.click();

    // The dialog validates the name and refuses to submit. It does not surface
    // the reason -- CreateWorkspaceDialog computes the error but never passes it
    // to the Field -- so all there is to assert is that nothing was created.
    await expect(workspaces.createDialog).toBeVisible();
    await expect(page).toHaveURL(
      new RegExp(`${organizationPaths.workspaces}$`),
    );
  });
});

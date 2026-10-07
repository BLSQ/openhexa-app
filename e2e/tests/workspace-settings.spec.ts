import { mergeTests } from "@playwright/test";

import { test as cleanupTest } from "../fixtures/cleanup";
import { expect, test as disposableTest } from "../fixtures/disposableWorkspace";
import { uniqueName } from "../helpers/confirm";
import { WorkspacePipelinesPage } from "../pages/WorkspacePipelinesPage";
import { WorkspaceSettingsPage } from "../pages/WorkspaceSettingsPage";

const test = mergeTests(cleanupTest, disposableTest);

const CONFIG_MARKER = "E2E-CONFIG";
const DATABASE_MARKER = "E2E-DATABASE-WRITTEN";

/**
 * Reports what a run sees of the workspace: its configuration, read through
 * the SDK, and its database, written with the credentials the run is given.
 */
const SETTINGS_PIPELINE_SOURCE = `from openhexa.sdk import current_run, pipeline, workspace
from sqlalchemy import create_engine, text


@pipeline("e2e_settings", name="E2E settings pipeline")
def e2e_settings():
    current_run.log_info(f"${CONFIG_MARKER} {workspace.configuration}")
    with create_engine(workspace.database_url).begin() as connection:
        connection.execute(text("CREATE TABLE IF NOT EXISTS e2e_settings (n integer)"))
    current_run.log_info("${DATABASE_MARKER}")


if __name__ == "__main__":
    e2e_settings()
`;

test.describe("Workspace settings", () => {
  test("its general settings change, and runs see them", async ({
    page,
    disposableWorkspace,
  }) => {
    // Provisioning a workspace, then a pipeline run in it.
    test.setTimeout(420_000);
    const settings = new WorkspaceSettingsPage(page);
    const pipelines = new WorkspacePipelinesPage(page);
    const configValue = uniqueName("e2e-value");

    const slug = await disposableWorkspace.create();
    const newName = `${disposableWorkspace.name} renamed`;

    await test.step("its name, countries and configuration are saved", async () => {
      await settings.gotoTab(slug, "General");
      await settings.editButton.click();
      await settings.field("Name").getByRole("textbox").fill(newName);
      await settings.addCountry("Senegal");
      await settings.addConfiguration("e2e_key", configValue);
      await settings.save();
      disposableWorkspace.renamed(newName);

      await settings.gotoTab(slug, "General");
      await expect(settings.field("Name")).toHaveText(newName);
      await expect(settings.field("Countries")).toContainText("Senegal");
      await expect(settings.field("Configuration")).toContainText("e2e_key");
      await expect(settings.field("Configuration")).toContainText(configValue);
    });

    await test.step("the database passwords are regenerated", async () => {
      await settings.gotoTab(slug, "Database");
      await settings.regeneratePassword("ro");
      await settings.regeneratePassword("rw");
    });

    await test.step("a run reads the configuration and writes to the database", async () => {
      const code = await pipelines.createWithSource(
        uniqueName("e2e-settings"),
        SETTINGS_PIPELINE_SOURCE,
        slug,
      );
      await page.goto(`/workspaces/${slug}/pipelines/${code}/`);
      await pipelines.run();

      expect(await pipelines.waitForRunToFinish()).toBe("Succeeded");
      await expect(page.getByText(new RegExp(`${CONFIG_MARKER} .*${configValue}`))).toBeVisible();
      // Written with the password regenerated above.
      await expect(page.getByText(DATABASE_MARKER)).toBeVisible();
    });
  });
});

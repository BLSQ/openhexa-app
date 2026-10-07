import { expect, test } from "../fixtures/cleanup";
import { uniqueName } from "../helpers/confirm";
import { WorkspaceDatabasePage } from "../pages/WorkspaceDatabasePage";
import { WorkspaceFilesPage } from "../pages/WorkspaceFilesPage";
import {
  RUN_PIPELINE_SOURCE,
  WorkspacePipelinesPage,
} from "../pages/WorkspacePipelinesPage";

test.describe("Workspace database", () => {
  test("the tables loaded for the suite are listed and open", async ({
    page,
  }) => {
    const database = new WorkspaceDatabasePage(page);

    await database.goto();
    await expect(database.rowCount("level_2_region")).toHaveText("14 rows");

    await database.tableRow("level_2_region").getByRole("link").first().click();
    await expect(database.columnHeader("name")).toBeVisible();
    await expect(page.getByRole("cell", { name: "Dakar" })).toBeVisible();
  });

  test("a table written by a pipeline is listed, opens, and is deleted", async ({
    page,
    cleanup,
  }) => {
    // A pipeline run, which provisions a container, writes the table.
    test.setTimeout(420_000);
    const pipelines = new WorkspacePipelinesPage(page);
    const database = new WorkspaceDatabasePage(page);
    const files = new WorkspaceFilesPage(page);
    const table = uniqueName("e2e_table").replace(/-/g, "_");

    const code = await pipelines.createWithSource(
      uniqueName("e2e-table"),
      RUN_PIPELINE_SOURCE,
    );
    cleanup.add(`pipeline ${code}`, () => pipelines.deleteIfPresent(code));
    cleanup.add(`file ${table}.csv`, () => files.deleteIfPresent(`${table}.csv`));
    cleanup.add(`table ${table}`, () => database.deleteTableIfPresent(table));

    await pipelines.gotoPipeline(code);
    await pipelines.runWith({ rows: 4, output: table });
    expect(await pipelines.waitForRunToFinish()).toBe("Succeeded");

    await test.step("the list shows it with its row count", async () => {
      await database.goto();
      await expect(database.rowCount(table)).toHaveText("4 rows");
    });

    await test.step("its page shows its columns and rows", async () => {
      await database.tableRow(table).getByRole("link", { name: "View" }).click();
      await expect(database.columnHeader("n")).toBeVisible();
      await expect(database.columnHeader("label")).toBeVisible();
      await expect(database.sampleRows).toHaveCount(4);
    });

    await test.step("deleting it removes it", async () => {
      await database.deleteTable(table);
      expect((await database.gotoTable(table))?.status()).toBe(404);
    });
  });
});

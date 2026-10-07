import { expect, test } from "../fixtures/cleanup";
import { uniqueName } from "../helpers/confirm";
import { WorkspaceDatabasePage } from "../pages/WorkspaceDatabasePage";
import { WorkspaceFilesPage } from "../pages/WorkspaceFilesPage";
import {
  HOLDING_MARKER,
  PARAMETERS_MARKER,
  RUN_PIPELINE_SOURCE,
  WorkspacePipelinesPage,
} from "../pages/WorkspacePipelinesPage";

// Each test waits for a pipeline container to be provisioned and run.
test.describe.configure({ timeout: 420_000 });

test.describe("Pipeline runs", () => {
  test("a run takes its parameters and lists its outputs", async ({
    page,
    cleanup,
  }) => {
    const pipelines = new WorkspacePipelinesPage(page);
    const database = new WorkspaceDatabasePage(page);
    const files = new WorkspaceFilesPage(page);
    // Doubles as a table name, so underscores rather than hyphens.
    const output = uniqueName("e2e_output").replace(/-/g, "_");
    const fileName = `${output}.csv`;

    const code = await pipelines.createWithSource(
      uniqueName("e2e-run"),
      RUN_PIPELINE_SOURCE,
    );
    cleanup.add(`pipeline ${code}`, () => pipelines.deleteIfPresent(code));
    cleanup.add(`file ${fileName}`, () => files.deleteIfPresent(fileName));
    cleanup.add(`table ${output}`, () =>
      database.deleteTableIfPresent(output),
    );

    await pipelines.gotoPipeline(code);
    await pipelines.runWith({ rows: 3, label: "beta", shout: true, output });

    expect(await pipelines.waitForRunToFinish()).toBe("Succeeded");

    await test.step("it shows the parameters it was given", async () => {
      await expect(pipelines.runDetail("Rows")).toHaveText("3");
      await expect(pipelines.runDetail("Label")).toHaveText("beta");
      await expect(
        pipelines.runDetail("Shout").getByRole("switch"),
      ).toHaveAttribute("aria-checked", "true");
      await expect(pipelines.runDetail("Output name")).toHaveText(output);
    });

    await test.step("and the pipeline received them", async () => {
      await expect(
        page.getByText(`${PARAMETERS_MARKER} rows=3 label=BETA`),
      ).toBeVisible();
    });

    await test.step("it lists the file and the table it wrote", async () => {
      await expect(pipelines.outputRow(fileName)).toContainText("File");
      await expect(pipelines.outputRow(output)).toBeVisible();
    });

    await test.step("the table output opens the table's rows", async () => {
      await pipelines.outputRow(output).getByRole("link").click();
      // The table page adds its sort order to the address.
      await page.waitForURL(new RegExp(`/databases/${output}/`));
      await expect(database.columnHeader("n")).toBeVisible();
      await expect(database.columnHeader("label")).toBeVisible();
      await expect(database.sampleRows).toHaveCount(3);
      await expect(database.sampleRows.first()).toContainText("BETA");
    });

    await test.step("the file output is in the workspace's files", async () => {
      await files.goto();
      await expect(files.row(fileName)).toBeVisible();
    });
  });

  test("a running run streams its messages and can be stopped", async ({
    page,
    cleanup,
  }) => {
    const pipelines = new WorkspacePipelinesPage(page);

    const code = await pipelines.createWithSource(
      uniqueName("e2e-run"),
      RUN_PIPELINE_SOURCE,
    );
    cleanup.add(`pipeline ${code}`, () => pipelines.deleteIfPresent(code));

    await pipelines.gotoPipeline(code);
    await pipelines.runWith({ hold: 600 });

    await test.step("messages arrive while it runs", async () => {
      await expect(page.getByText(`${HOLDING_MARKER} 0s`)).toBeVisible({
        timeout: 300_000,
      });
      // The next one is only logged five seconds later, so seeing it without
      // a reload means the page is following the run.
      await expect(page.getByText(`${HOLDING_MARKER} 10s`)).toBeVisible({
        timeout: 60_000,
      });
      await expect(pipelines.runStatus).toContainText("Started on");
    });

    await test.step("stopping it ends it as Stopped", async () => {
      await pipelines.stopRun();
      expect(await pipelines.waitForRunToFinish(120_000)).toBe("Stopped");
      await expect(pipelines.runDetail("Stopped by")).not.toBeEmpty();
      await expect(pipelines.stopButton).toHaveCount(0);
      await expect(
        page.getByRole("button", { name: "Run again" }),
      ).toBeVisible();
    });
  });
});

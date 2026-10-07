import { expect, test } from "../fixtures/cleanup";
import { uniqueName } from "../helpers/confirm";
import { PipelineDetailPage } from "../pages/PipelineDetailPage";
import {
  EDITED_PIPELINE_SOURCE,
  PARAMETERS_MARKER,
  RUN_PIPELINE_SOURCE,
  WorkspacePipelinesPage,
} from "../pages/WorkspacePipelinesPage";

test.describe("Pipeline settings", () => {
  let pipelines: WorkspacePipelinesPage;
  let pipeline: PipelineDetailPage;
  let code: string;

  test.beforeEach(async ({ page, cleanup }) => {
    pipelines = new WorkspacePipelinesPage(page);
    code = await pipelines.createWithSource(
      uniqueName("e2e-settings"),
      RUN_PIPELINE_SOURCE,
    );
    cleanup.add(`pipeline ${code}`, () => pipelines.deleteIfPresent(code));
    pipeline = new PipelineDetailPage(page, code);
  });

  test("its name, description, tags and type are edited", async () => {
    const name = uniqueName("E2E renamed");
    const description = uniqueName("Described by the e2e suite");
    const tag = uniqueName("e2e-tag");

    await pipeline.gotoGeneral();
    await pipeline.editInformation({
      name,
      description,
      tag,
      type: "Transformation",
    });

    await pipeline.gotoGeneral();
    await expect(pipeline.heading).toHaveText(name);
    await expect(pipeline.field("Description")).toContainText(description);
    await expect(pipeline.field("Tags")).toContainText(tag);
    await expect(pipeline.field("Type")).toContainText("Transformation");
    // The code a pipeline is reached by does not follow its name.
    await expect(pipeline.field("Code")).toHaveText(code);
  });

  test("a schedule is checked, saved and turned off; recipients are kept", async ({
    page,
  }) => {
    await pipeline.gotoScheduling();

    await test.step("an invalid schedule is refused", async () => {
      await pipeline.startScheduling("not a schedule");
      await expect(pipeline.field("Schedule")).toContainText("Invalid");
      await page.reload();
    });

    await test.step("a valid one is saved", async () => {
      await pipeline.startScheduling("0 3 * * *");
      await expect(pipeline.field("Schedule")).toContainText("Next run");
      await pipeline.save();

      await pipeline.gotoScheduling();
      await expect(
        pipeline.field("Enabled").getByRole("switch"),
      ).toHaveAttribute("aria-checked", "true");
      // Read back in words, not as the expression typed.
      await expect(pipeline.field("Schedule")).toContainText("At 03:00 AM (UTC)");
    });

    await test.step("and turned off again", async () => {
      await pipeline.stopScheduling();
    });

    await test.step("a recipient is added and removed", async () => {
      const name = await pipeline.addRecipient("Error");
      await pipeline.gotoScheduling();
      await expect(pipeline.recipientRow(name)).toContainText("Error");

      await pipeline.removeRecipient(name);
      await pipeline.gotoScheduling();
      await expect(pipeline.recipientRow(name)).toHaveCount(0);
    });
  });

  test("its webhook starts a run, and a new URL replaces the old", async ({
    page,
  }) => {
    test.setTimeout(300_000);
    await pipeline.gotoGeneral();
    await pipeline.setWebhookEnabled(true);
    const url = (await pipeline.webhookUrl.innerText()).trim();
    expect(url).toMatch(/^https?:\/\//);

    await test.step("a POST to it starts a run", async () => {
      // The webhook refuses a body without a content type.
      const response = await page.request.post(url, { data: {} });
      expect(response.ok(), await response.text()).toBe(true);

      await pipeline.gotoRuns();
      await expect(pipeline.runRows.first()).toContainText("Webhook");
      await pipeline.runRows.first().getByRole("link").first().click();
      await pipelines.waitForRunToFinish();
      await expect(pipelines.runDetail("Trigger")).toHaveText("Webhook");
    });

    await test.step("regenerating it retires the old URL", async () => {
      await pipeline.gotoGeneral();
      await pipeline.regenerateWebhookUrl();
      await pipeline.gotoGeneral();
      await expect(pipeline.webhookUrl).not.toHaveText(url);

      const stale = await page.request.post(url, { data: {} });
      expect(stale.ok()).toBe(false);
    });

    await test.step("disabling it hides the URL", async () => {
      await pipeline.setWebhookEnabled(false);
      await expect(pipeline.webhookUrl).toHaveCount(0);
    });
  });

  test("default values prefill a run; versions are edited and deleted", async ({
    page,
  }) => {
    test.setTimeout(300_000);
    const versionName = uniqueName("e2e version");
    const versionDescription = uniqueName("Version described by the e2e suite");

    await test.step("defaults are saved and offered by the run dialog", async () => {
      await pipeline.gotoGeneral();
      await pipeline.openDefaults();
      await pipelines.fillParameters({ rows: 5, label: "beta" }, pipeline.defaultsDialog);
      await pipeline.saveDefaults();

      await pipeline.gotoGeneral();
      await expect(pipeline.parameterRow("rows")).toContainText("5");
      await expect(pipeline.parameterRow("label")).toContainText("beta");

      await pipelines.runButton.click();
      await expect(
        pipelines.parameterField("rows").getByRole("spinbutton"),
      ).toHaveValue("5");
      await pipelines.runDialog.getByRole("button", { name: "Run", exact: true }).click();
      await page.waitForURL(/\/runs\/[0-9a-f-]{36}\/?$/);
      expect(await pipelines.waitForRunToFinish()).toBe("Succeeded");
      await expect(
        page.getByText(`${PARAMETERS_MARKER} rows=5 label=beta`),
      ).toBeVisible();
    });

    await test.step("the runs tab lists the run", async () => {
      await pipeline.gotoRuns();
      await expect(pipeline.runRows).toHaveCount(1);
      await expect(pipeline.runRows.first()).toContainText("Manual");
      await expect(pipeline.runRows.first()).toContainText("Succeeded");
      // The version column names the current version "Latest".
      await expect(pipeline.runRows.first()).toContainText("Latest");
    });

    await test.step("a version's name and description are edited", async () => {
      await pipeline.gotoVersions();
      await pipeline.editVersion("v1", {
        name: versionName,
        description: versionDescription,
      });
      await page.reload();
      // A named version goes by its name rather than its number.
      await expect(pipeline.versionCard(versionName)).toContainText(
        versionDescription,
      );
    });

    await test.step("its code and a version download as zips", async () => {
      const [download] = await Promise.all([
        page.waitForEvent("download"),
        pipeline
          .versionCard(versionName)
          .getByRole("button", { name: "Download" })
          .click(),
      ]);
      expect(download.suggestedFilename()).toMatch(/\.zip$/);

      await pipeline.gotoGeneral();
      const [codeDownload] = await Promise.all([
        page.waitForEvent("download"),
        page.getByRole("button", { name: "Download code" }).click(),
      ]);
      expect(codeDownload.suggestedFilename()).toMatch(/\.zip$/);
    });

    await test.step("an older version is deleted", async () => {
      await pipelines.uploadVersion(code, EDITED_PIPELINE_SOURCE);
      await pipeline.gotoVersions();
      await expect(pipeline.versionCard("v2")).toBeVisible();

      await pipeline.deleteVersion(versionName);
      await page.reload();
      await expect(pipeline.versionCard(versionName)).toHaveCount(0);
      await expect(pipeline.versionCard("v2")).toBeVisible();
    });
  });
});

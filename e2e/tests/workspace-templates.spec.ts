import { expect, test } from "../fixtures/cleanup";
import { uniqueName } from "../helpers/confirm";
import { PipelineDetailPage } from "../pages/PipelineDetailPage";
import {
  EDITED_PIPELINE_SOURCE,
  RUN_PIPELINE_SOURCE,
  WorkspacePipelinesPage,
} from "../pages/WorkspacePipelinesPage";
import { WorkspaceTemplatesPage } from "../pages/WorkspaceTemplatesPage";

test.describe("Pipeline templates", () => {
  test("a template is published, used, upgraded and deleted", async ({
    page,
    cleanup,
  }) => {
    test.setTimeout(300_000);
    const pipelines = new WorkspacePipelinesPage(page);
    const templates = new WorkspaceTemplatesPage(page);
    // Lower-case and hyphenated, so the template's code and that of the
    // pipeline built from it are both this name.
    const name = uniqueName("e2e-template");
    const description = uniqueName("Published by the e2e suite");

    const source = await pipelines.createWithSource(
      uniqueName("e2e-template-source"),
      RUN_PIPELINE_SOURCE,
    );
    cleanup.add(`pipeline ${source}`, () => pipelines.deleteIfPresent(source));
    cleanup.add(`template ${name}`, () => templates.deleteIfPresent(name, name));

    const code = await test.step("the pipeline is published", async () => {
      await pipelines.gotoPipeline(source);
      const code = await templates.publishNew(name, description);
      if (code !== name) {
        cleanup.add(`template ${code}`, () =>
          templates.deleteIfPresent(code, name),
        );
      }
      await expect(templates.heading).toHaveText(name);
      await expect(page.getByText(description)).toBeVisible();
      return code;
    });

    await test.step("its code and versions pages render", async () => {
      // A template version is named after the template unless told otherwise.
      await templates.gotoTemplate(code, "code/");
      await expect(
        page.getByRole("heading", { name: `Files - ${name}` }),
      ).toBeVisible();
      await expect(page.locator(".cm-content")).toContainText("e2e_run");
      await templates.gotoTemplate(code, "versions/");
      // Its versions page numbers them instead.
      await expect(
        page.getByRole("heading", { name: /^Version 1\b/ }),
      ).toBeVisible();
    });

    const built = await test.step("the catalogue offers it to build a pipeline", async () => {
      const built = await templates.createPipelineFrom(name);
      cleanup.add(`pipeline ${built}`, () => pipelines.deleteIfPresent(built));
      const pipeline = new PipelineDetailPage(page, built);
      await pipeline.gotoGeneral();
      await expect(pipeline.field("Source")).toHaveText("Template");
      await expect(pipeline.field("Source Template")).toContainText(name);
      return built;
    });

    await test.step("a new template version upgrades that pipeline", async () => {
      await pipelines.uploadVersion(source, EDITED_PIPELINE_SOURCE);
      await pipelines.gotoPipeline(source);
      await templates.publishVersion(name, "e2e: a second version");
      await templates.gotoTemplate(code, "versions/");
      await expect(page.getByText("e2e: a second version")).toBeVisible();

      await pipelines.gotoPipeline(built);
      await templates.upgradePipeline();
      await pipelines.gotoVersions(built);
      await expect(pipelines.versionHeading("v2")).toBeVisible();
    });

    await test.step("deleting it takes it out of the catalogue", async () => {
      await templates.gotoTemplate(code);
      await templates.delete(name);
      expect((await templates.gotoTemplate(code))?.status()).toBe(404);
    });
  });
});

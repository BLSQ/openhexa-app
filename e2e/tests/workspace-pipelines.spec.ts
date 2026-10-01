import { expect, test } from "../fixtures/cleanup";
import {
  EDITED_PIPELINE_MARKER,
  EDITED_PIPELINE_SOURCE,
  PIPELINE_TABS,
  WorkspacePipelinesPage,
} from "../pages/WorkspacePipelinesPage";

// A pipeline built from a template takes the template's name, so two of these
// tests running at once would collide over the same pipeline code.
test.describe.configure({ mode: "serial" });

test.describe("Workspace pipelines", () => {
  test("a pipeline can be created from a template and deleted", async ({
    page,
    cleanup,
  }) => {
    const pipelines = new WorkspacePipelinesPage(page);

    const { name, code } = await pipelines.createFromFirstTemplate();
    cleanup.add(`pipeline ${code}`, () => pipelines.deleteIfPresent(code));

    expect(code).toBeTruthy();
    await expect(page).toHaveTitle(`OpenHEXA | ${name}`);

    await pipelines.goto();
    await expect(pipelines.row(name)).toBeVisible();

    await pipelines.gotoPipeline(code);
    await pipelines.delete();
    await expect(pipelines.row(name)).toHaveCount(0);
  });

  test("a pipeline runs, and runs the new version once its code is edited", async ({
    page,
    cleanup,
  }) => {
    // Two pipeline runs, each of which provisions a container.
    test.setTimeout(600_000);

    const pipelines = new WorkspacePipelinesPage(page);
    const { name, code } = await pipelines.createFromFirstTemplate();
    cleanup.add(`pipeline ${code}`, () => pipelines.deleteIfPresent(code));

    await test.step("every tab renders", async () => {
      for (const tab of PIPELINE_TABS) {
        await pipelines.gotoPipeline(code);
        await pipelines.openTab(tab);
        await expect(
          page.getByRole("heading", { name, level: 2 }),
        ).toBeVisible();
      }

      await pipelines.gotoVersions(code);
      await expect(
        page.getByRole("heading", { name: /Version v1/ }),
      ).toBeVisible();
    });

    await test.step("the pipeline as created runs to completion", async () => {
      await pipelines.gotoPipeline(code);
      await pipelines.run();

      // The template's own code may well fail -- it is third-party and most
      // templates call out to a real service -- so this checks that the run
      // machinery carries it to a verdict, not which verdict it reaches.
      const status = await pipelines.waitForRunToFinish();
      expect(
        ["Succeeded", "Failed"],
        `the first run ended as ${status}`,
      ).toContain(status);
      await expect(pipelines.runDetail("Version")).toHaveText("v1");
    });

    await test.step("editing the code publishes a second version", async () => {
      await pipelines.editCode(code, EDITED_PIPELINE_SOURCE);
      await expect(pipelines.filesHeading("v2")).toBeVisible();
    });

    await test.step("the next run uses the edited version", async () => {
      await pipelines.gotoPipeline(code);
      await pipelines.run();

      expect(await pipelines.waitForRunToFinish()).toBe("Succeeded");
      await expect(pipelines.runDetail("Version")).toHaveText("v2");
      // Proof it ran the new code rather than reporting a new version number.
      await expect(pipelines.runMessages).toContainText(EDITED_PIPELINE_MARKER);
    });
  });
});

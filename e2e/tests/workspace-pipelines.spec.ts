import { expect, test } from "../fixtures/cleanup";
import { WorkspacePipelinesPage } from "../pages/WorkspacePipelinesPage";

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
});

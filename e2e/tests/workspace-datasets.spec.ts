import { expect, test } from "../fixtures/cleanup";
import { uniqueName } from "../helpers/confirm";
import { WorkspaceDatasetsPage } from "../pages/WorkspaceDatasetsPage";

test.describe("Workspace datasets", () => {
  test("a dataset and a version can be created and removed", async ({
    page,
    cleanup,
  }) => {
    const datasets = new WorkspaceDatasetsPage(page);
    const name = uniqueName("e2e dataset");

    await datasets.goto();
    const slug = await datasets.create(name, "Created by the e2e suite.");
    cleanup.add(`dataset ${slug}`, () => datasets.deleteIfPresent(slug));

    expect(slug).toBeTruthy();
    await expect(page.getByRole("heading", { name, level: 2 })).toBeVisible();

    // Deleting the dataset would take the version with it, but the version has
    // its own removal path and this checks it works on its own.
    await datasets.createVersion("v1", "sample.csv");
    await datasets.deleteVersion();

    await datasets.deleteDataset();
    await expect(datasets.row(name)).toHaveCount(0);
  });
});

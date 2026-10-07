import { mergeTests } from "@playwright/test";

import { test as cleanupTest } from "../fixtures/cleanup";
import { expect, test as disposableTest } from "../fixtures/disposableWorkspace";
import { uniqueName } from "../helpers/confirm";
import { OrganizationDatasetsPage } from "../pages/OrganizationDatasetsPage";
import { WorkspaceDatasetsPage } from "../pages/WorkspaceDatasetsPage";

const test = mergeTests(cleanupTest, disposableTest);

const FIRST_VERSION = "district,cases\nDakar,12\nThiès,7\nSaint-Louis,3\n";
const SECOND_VERSION = "district,cases\nKaolack,20\nZiguinchor,4\n";

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

  test("a version's file is previewed, profiled and downloaded", async ({
    page,
    cleanup,
  }) => {
    const datasets = new WorkspaceDatasetsPage(page);

    await datasets.goto();
    const slug = await datasets.create(uniqueName("e2e dataset"), "Profiled.");
    cleanup.add(`dataset ${slug}`, () => datasets.deleteIfPresent(slug));
    await datasets.createVersion("v1", "cases.csv", FIRST_VERSION);
    await datasets.createVersion("v2", "cases.csv", SECOND_VERSION);

    await test.step("the latest version's rows are previewed", async () => {
      await datasets.openTab("Files");
      await expect(datasets.versionPicker).toHaveText(/^v2 - /);
      await expect(datasets.field("Rows in dataset")).toHaveText("2");
      await expect(datasets.previewTable).toContainText("Kaolack");
    });

    await test.step("each column is profiled", async () => {
      await page.getByRole("tab", { name: "Columns" }).click();
      await expect(datasets.columnStatistics("district")).toContainText(
        "Distinct2 (100%)",
      );
      await expect(page.getByRole("row", { name: "Maximum 20" })).toBeVisible();
    });

    await test.step("the file downloads", async () => {
      const [download] = await Promise.all([
        page.waitForEvent("download"),
        datasets.fileDownloadButton.click(),
      ]);
      expect(download.suggestedFilename()).toBe("cases.csv");
    });

    await test.step("an earlier version is picked", async () => {
      await datasets.pickVersion("v1");
      await page.getByRole("tab", { name: "Preview" }).click();
      await expect(datasets.field("Rows in dataset")).toHaveText("3");
      await expect(datasets.previewTable).toContainText("Dakar");
    });
  });

  test("a dataset is renamed and shared with the organization", async ({
    page,
    cleanup,
  }) => {
    const datasets = new WorkspaceDatasetsPage(page);
    const organizationDatasets = new OrganizationDatasetsPage(page);
    const name = uniqueName("e2e renamed dataset");
    const description = uniqueName("Re-described by the e2e suite");

    await datasets.goto();
    const slug = await datasets.create(uniqueName("e2e dataset"), "Original.");
    cleanup.add(`dataset ${slug}`, () => datasets.deleteIfPresent(slug));

    await test.step("its name and description are edited", async () => {
      await datasets.edit(name, description);
      await page.reload();
      await expect(page.getByRole("heading", { level: 2 })).toContainText(name);
      await expect(datasets.field("Description")).toContainText(description);
      // The slug it is reached by does not follow the name.
      await expect(datasets.field("Identifier")).toContainText(slug);
    });

    await test.step("the organization lists it by where it is shared", async () => {
      await organizationDatasets.goto();
      await organizationDatasets.search(name);
      await expect(organizationDatasets.row(name)).toContainText(
        "Source workspace only",
      );
    });

    await test.step("shared with the organization, it says so", async () => {
      await datasets.gotoDataset(slug);
      await datasets.openTab("Access management");
      await datasets.setSharedWithOrganization(true);

      await organizationDatasets.goto();
      await organizationDatasets.search(name);
      await expect(organizationDatasets.row(name)).toContainText("Organization");

      await datasets.gotoDataset(slug);
      await datasets.openTab("Access management");
      await datasets.setSharedWithOrganization(false);
    });
  });

  test("a dataset shared with another workspace is read there", async ({
    page,
    cleanup,
    disposableWorkspace,
  }) => {
    test.setTimeout(240_000);
    const datasets = new WorkspaceDatasetsPage(page);

    const otherSlug = await disposableWorkspace.create();

    await datasets.goto();
    const name = uniqueName("e2e shared dataset");
    const slug = await datasets.create(name, "Shared.");
    cleanup.add(`dataset ${slug}`, () => datasets.deleteIfPresent(slug));
    await datasets.createVersion("v1", "cases.csv", FIRST_VERSION);

    await datasets.openTab("Access management");
    await datasets.shareWithWorkspace(disposableWorkspace.name);

    await test.step("the other workspace lists it and can read it", async () => {
      await page.goto(`/workspaces/${otherSlug}/datasets/`);
      await page.getByRole("link", { name, exact: true }).click();
      await datasets.openTab("Files");
      await expect(datasets.previewTable).toContainText("Dakar");
      await expect(datasets.newVersionButton).toHaveCount(0);
    });

    await test.step("revoking the link takes it away", async () => {
      await datasets.gotoDataset(slug);
      await datasets.openTab("Access management");
      await datasets.revokeLink(disposableWorkspace.name);

      await page.goto(`/workspaces/${otherSlug}/datasets/`);
      await expect(page.getByRole("columnheader", { name: "Name" })).toBeVisible();
      await page.waitForLoadState("networkidle");
      await expect(page.getByRole("link", { name, exact: true })).toHaveCount(0);
    });
  });
});

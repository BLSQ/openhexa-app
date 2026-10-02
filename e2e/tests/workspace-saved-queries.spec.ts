import { expect, test } from "../fixtures/cleanup";
import { uniqueName } from "../helpers/confirm";
import { WorkspaceDataStudioPage } from "../pages/WorkspaceDataStudioPage";

const REGIONS_SQL = "SELECT code, name FROM level_2_region ORDER BY code";
const DEPARTMENTS_SQL =
  "SELECT code, name FROM level_3_department ORDER BY code";

test.describe("Workspace saved queries", () => {
  test("a saved query is listed, opens, and can be deleted", async ({
    page,
    cleanup,
  }) => {
    const studio = new WorkspaceDataStudioPage(page);
    const name = uniqueName("e2e query");
    const description = "Regions of Senegal, by code.";

    const slug = await studio.create(REGIONS_SQL, {
      name,
      description,
      sharing: "Private",
    });
    cleanup.add(`saved query ${slug}`, () => studio.deleteIfPresent(slug));

    await test.step("the query page shows it", async () => {
      await expect(page).toHaveTitle(`OpenHEXA | ${name}`);
      await expect(studio.queryName(slug)).toHaveText(name);
      await expect(studio.sqlEditor).toHaveText(REGIONS_SQL);
      await expect(studio.sharingButton("Private")).toBeVisible();
    });

    await test.step("the list shows it", async () => {
      await studio.gotoList(name);
      await expect(studio.cell(slug, "Name")).toContainText(name);
      await expect(studio.cell(slug, "Description")).toHaveText(description);
      await expect(studio.cell(slug, "Visibility")).toHaveText("Private");
    });

    await test.step("a row opens the query, and runs it", async () => {
      await studio.row(slug).click();
      await page.waitForURL(`**/queries/${slug}/`);
      await studio.runButton.click();
      await expect(studio.resultSummary).toHaveText(/^14 rows/);
    });

    await test.step("deleting it removes it from the list", async () => {
      await studio.gotoList(name);
      await studio.deleteFromList(slug);
      await expect(studio.row(slug)).toHaveCount(0);
      const response = await studio.gotoQuery(slug);
      expect(response?.status()).toBe(404);
    });
  });

  test("a saved query's details, SQL and sharing can be changed", async ({
    page,
    cleanup,
  }) => {
    const studio = new WorkspaceDataStudioPage(page);

    const slug = await studio.create(REGIONS_SQL, {
      name: uniqueName("e2e query"),
      description: "Before the edit.",
      sharing: "Private",
    });
    cleanup.add(`saved query ${slug}`, () => studio.deleteIfPresent(slug));

    const renamed = uniqueName("e2e renamed");
    const description = "After the edit: departments, by code.";

    await test.step("its details are edited and it is shared", async () => {
      await studio.editDetails({
        name: renamed,
        description,
        sharing: "Workspace",
      });
      await expect(studio.queryName(slug)).toHaveText(renamed);
      await expect(studio.sharingButton("Workspace")).toBeVisible();
    });

    await test.step("its SQL is edited and saved in place", async () => {
      await studio.saveSql(DEPARTMENTS_SQL);
    });

    await test.step("the edits survive a reload", async () => {
      await studio.gotoQuery(slug);
      await expect(studio.queryName(slug)).toHaveText(renamed);
      await expect(studio.sqlEditor).toHaveText(DEPARTMENTS_SQL);
      await expect(studio.sharingButton("Workspace")).toBeVisible();

      await studio.gotoList(renamed);
      await expect(studio.cell(slug, "Name")).toContainText(renamed);
      await expect(studio.cell(slug, "Description")).toHaveText(description);
      await expect(studio.cell(slug, "Visibility")).toHaveText("Workspace");
    });

    await test.step("it is made private again from the toolbar", async () => {
      await studio.gotoQuery(slug);
      await studio.makePrivate();

      await studio.gotoList(renamed);
      await expect(studio.cell(slug, "Visibility")).toHaveText("Private");
    });
  });
});

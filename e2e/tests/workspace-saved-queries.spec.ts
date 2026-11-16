import { BASE_URL, workspacePaths } from "../config/environment";
import { expect, test } from "../fixtures/visitors";
import { uniqueName } from "../helpers/confirm";
import { PublicSavedQueryPage } from "../pages/PublicSavedQueryPage";
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

    await test.step("the list finds it by its slug too", async () => {
      // The slug is not the name: it has no space in it.
      expect(slug).not.toBe(name);
      await studio.gotoList(slug);
      await expect(studio.row(slug)).toBeVisible();
    });

    await test.step("a row opens the query, and runs it", async () => {
      await studio.openFromList(slug);
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

  test("a public query is read by anyone with its link, until it is taken back", async ({
    page,
    anonymousPage,
    cleanup,
  }) => {
    test.setTimeout(180_000);
    const studio = new WorkspaceDataStudioPage(page);
    const visitor = new PublicSavedQueryPage(anonymousPage);
    const name = uniqueName("e2e public query");
    const description = "Regions of Senegal, for anyone.";

    const slug = await studio.create(REGIONS_SQL, {
      name,
      description,
      sharing: "Workspace",
    });
    cleanup.add(`saved query ${slug}`, () => studio.deleteIfPresent(slug));
    const link = new URL(PublicSavedQueryPage.path(slug), BASE_URL).href;

    await test.step("a query that is not public has no link", async () => {
      await expect(studio.publicLinkButton).toHaveCount(0);

      await visitor.goto(slug);
      await expect(anonymousPage).toHaveURL(/\/login\/?\?next=/);
    });

    await test.step("making it public hands out its link", async () => {
      await studio.makePublic("Workspace");
      expect(await studio.copyPublicLink()).toBe(link);

      await studio.gotoList(name);
      await expect(studio.cell(slug, "Visibility")).toHaveText("Public");
      await expect(studio.publicLink(slug)).toHaveAttribute("href", link);
    });

    await test.step("a visitor without an account sees its result, not its SQL", async () => {
      await visitor.goto(slug);
      await expect(anonymousPage).toHaveTitle(`OpenHEXA | ${name}`);
      await expect(visitor.heading(name)).toBeVisible();
      await expect(visitor.text(description)).toBeVisible();
      await expect(visitor.resultSummary).toHaveText(/^14 rows/);
      await expect(visitor.resultRow("Dakar")).toBeVisible();

      await expect(visitor.loginLink).toBeVisible();
      await expect(visitor.openInDataStudioLink).toHaveCount(0);
      await expect(visitor.text("level_2_region")).toHaveCount(0);
    });

    await test.step("the visitor downloads the full result", async () => {
      const lines = (await visitor.exportCsv()).trim().split(/\r?\n/);
      expect(lines[0]).toBe("code,name");
      expect(lines).toHaveLength(15);
    });

    await test.step("a member is led back to the Data Studio", async () => {
      const member = new PublicSavedQueryPage(page);
      await member.goto(slug);
      await expect(member.resultSummary).toHaveText(/^14 rows/);
      await expect(member.loginLink).toHaveCount(0);

      await member.openInDataStudioLink.click();
      await page.waitForURL(`**${workspacePaths.savedQueries}${slug}/`);
      await expect(studio.sqlEditor).toHaveText(REGIONS_SQL);
    });

    await test.step("taken back to the workspace, its link stops working", async () => {
      await studio.stopSharingPublicly();
      await expect(studio.publicLinkButton).toHaveCount(0);

      await visitor.goto(slug);
      await expect(anonymousPage).toHaveURL(/\/login\/?\?next=/);

      // A member is sent to where they work with it instead.
      await page.goto(PublicSavedQueryPage.path(slug));
      await expect(page).toHaveURL(
        new RegExp(`${workspacePaths.savedQueries}${slug}/?$`),
      );
    });
  });
});

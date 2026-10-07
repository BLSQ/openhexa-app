import { workspace, workspacePaths } from "../config/environment";
import { expect, test } from "../fixtures/cleanup";
import { uniqueName } from "../helpers/confirm";
import { GlobalSearch } from "../pages/GlobalSearch";
import {
  RUN_PIPELINE_SOURCE,
  WorkspacePipelinesPage,
} from "../pages/WorkspacePipelinesPage";
import { WorkspaceSections } from "../pages/WorkspaceSections";

/** Each sidebar entry and where it leads. "Data Studio" carries a badge. */
const SIDEBAR: { label: string | RegExp; path: string }[] = [
  { label: "Home", path: workspacePaths.home },
  { label: "Files", path: workspacePaths.files },
  { label: "Database", path: workspacePaths.home.replace(/\/$/, "/databases/") },
  { label: /^Data Studio/, path: workspacePaths.dataStudio },
  { label: "Datasets", path: workspacePaths.datasets },
  { label: "Connections", path: workspacePaths.connections },
  { label: "Pipelines", path: workspacePaths.pipelines },
  { label: "JupyterHub", path: workspacePaths.home.replace(/\/$/, "/notebooks/") },
  { label: "Apps", path: workspacePaths.webapps },
  { label: "Settings", path: workspacePaths.settings },
];

test.describe("Workspace navigation", () => {
  test("the home page greets the workspace", async ({ page }) => {
    await page.goto(workspacePaths.home);
    await expect(
      page.getByRole("heading", { name: workspace.name, level: 1 }),
    ).toBeVisible();
    await expect(page).toHaveTitle(`OpenHEXA | ${workspace.name}`);
  });

  test("the sidebar leads to every section", async ({ page }) => {
    const sections = new WorkspaceSections(page, workspace.slug);

    for (const { label, path } of SIDEBAR) {
      await page.goto(workspacePaths.home);
      await sections.sidebar.getByRole("link", { name: label }).click();
      await page.waitForURL(`**${path}**`);
    }
  });

  test("the search finds a table and a pipeline", async ({ page, cleanup }) => {
    const search = new GlobalSearch(page);
    const pipelines = new WorkspacePipelinesPage(page);
    const name = uniqueName("e2e-searchable");

    const code = await pipelines.createWithSource(name, RUN_PIPELINE_SOURCE);
    cleanup.add(`pipeline ${code}`, () => pipelines.deleteIfPresent(code));

    await test.step("a table loaded for the suite", async () => {
      await page.goto(workspacePaths.home);
      await search.search("level_2_region");
      await expect(search.tab("Tables")).toHaveText("Tables (1)");
      await search.resultLink("level_2_region").click();
      await page.waitForURL(/\/databases\/level_2_region\//);
    });

    await test.step("a pipeline created just now", async () => {
      await page.goto(workspacePaths.home);
      await search.search(name);
      await search.tab("Pipelines").click();
      await search.resultLink(name).click();
      await page.waitForURL(`**/pipelines/${code}/`);
    });
  });

  test("the retired top-level pages lead to the workspaces", async ({ page }) => {
    for (const path of ["/pipelines/", "/notebooks/"]) {
      await page.goto(path);
      await expect(page, `${path} lands on a workspace`).toHaveURL(
        /\/workspaces\//,
      );
    }
  });
});

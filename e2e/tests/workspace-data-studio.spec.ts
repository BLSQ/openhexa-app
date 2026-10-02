import { expect, test } from "@playwright/test";

import { WorkspaceDataStudioPage } from "../pages/WorkspaceDataStudioPage";

// These read the Senegal boundaries and bike counts loaded into the test
// workspace's database, so the values asserted are that data's.
const DEPARTMENTS_PER_REGION = `
  SELECT r.name AS {label}, COUNT(*) AS {value}
  FROM level_3_department d
  JOIN level_2_region r ON r.ref = d.parent_ref
  GROUP BY r.name
  ORDER BY {value} DESC, r.name`;

const departmentsPerRegion = (label: string, value: string) =>
  DEPARTMENTS_PER_REGION.replaceAll("{label}", label).replaceAll(
    "{value}",
    value,
  );

test.describe("Workspace Data Studio", () => {
  test("a query shows its rows in a table", async ({ page }) => {
    const studio = new WorkspaceDataStudioPage(page);
    await studio.goto();

    await studio.run("SELECT code, name FROM level_2_region ORDER BY code");

    await expect(studio.resultSummary).toHaveText(/^14 rows/);
    await expect(
      studio.resultsTable.getByRole("columnheader", { name: "code" }),
    ).toBeVisible();
    await expect(
      studio.resultsTable.getByRole("columnheader", { name: "name" }),
    ).toBeVisible();

    await expect(studio.resultCells(1)).toHaveText(["1", "SN.DB", "Diourbel"]);
    await expect(studio.resultCells("last")).toHaveText([
      "14",
      "SN.ZG",
      "Ziguinchor",
    ]);

    // A plain result has no widget to switch to.
    await expect(studio.resultTabs).toHaveCount(0);
  });

  test("a failing query says why", async ({ page }) => {
    const studio = new WorkspaceDataStudioPage(page);
    await studio.goto();

    await studio.run("SELECT * FROM e2e_no_such_table");

    await expect(studio.queryError).toBeVisible();
    await expect(
      studio.queryErrorDetail('relation "e2e_no_such_table" does not exist'),
    ).toBeVisible();
  });

  test("bar_label and bar_quantity draw a bar chart", async ({ page }) => {
    const studio = new WorkspaceDataStudioPage(page);
    await studio.goto();

    await studio.run(departmentsPerRegion("bar_label", "bar_quantity"));

    await expect(studio.resultTab("Chart")).toHaveAttribute(
      "aria-selected",
      "true",
    );
    await expect(studio.bar("Dakar")).toContainText("4");
    await expect(studio.bar("Ziguinchor")).toContainText("3");

    await studio.resultTab("Table").click();
    await expect(studio.resultsTable).toBeVisible();
    await expect(studio.resultSummary).toHaveText(/^14 rows/);
  });

  test("line_x and line_y draw a line chart", async ({ page }) => {
    const studio = new WorkspaceDataStudioPage(page);
    await studio.goto();

    // 88 points: past the default 50 rows, which would cut the series short.
    await studio.maxRows.selectOption("100");
    await studio.run(`
      SELECT "Time gap" AS line_x, SUM("Count") AS line_y
      FROM bikes_history
      GROUP BY "Time gap"
      ORDER BY "Time gap"`);

    await expect(studio.resultTab("Chart")).toHaveAttribute(
      "aria-selected",
      "true",
    );
    await expect(studio.lineChart).toBeVisible();
    // The x axis labels the first, middle and last points.
    await expect(studio.lineXLabels).toHaveText(["1", "44", "88"]);
    await expect(studio.resultSummary).toHaveText(/^88 rows/);
  });

  test("pie_label and pie_quantity draw a pie chart", async ({ page }) => {
    const studio = new WorkspaceDataStudioPage(page);
    await studio.goto();

    await studio.run(departmentsPerRegion("pie_label", "pie_quantity"));

    await expect(studio.pieChart).toBeVisible();
    // 14 regions: the first five keep a slice and the rest fold into "Other".
    await expect(studio.pieSlices).toHaveCount(6);
    await expect(studio.pieSlice("Dakar")).toContainText("8.9%");
    await expect(studio.pieSlice("Other")).toContainText("27");
    await expect(studio.pieSlice("Other")).toContainText("60.0%");
  });

  test("map_geometry draws shapes on a map", async ({ page }) => {
    const studio = new WorkspaceDataStudioPage(page);
    await studio.goto();

    await studio.run(`
      SELECT name, code, ST_AsGeoJSON(geom) AS map_geometry
      FROM level_3_department`);

    await expect(studio.resultTab("Map")).toHaveAttribute(
      "aria-selected",
      "true",
    );
    await expect(studio.resultSummary).toHaveText(/^45 rows/);

    // The data only reaches the map through MapLibre's worker, which fails
    // silently and leaves a bare basemap; a popup proves the shapes are there.
    await studio.clickMapCentre("name");
    await expect(studio.mapPopupValue("name")).toHaveText("Koupentoum");
    await expect(studio.mapPopupValue("code")).toHaveText("SN.TB.KP");
  });
});

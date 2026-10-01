import { Page } from "@playwright/test";

/**
 * The data grids render "No elements to display" while they are still loading,
 * so reading a row count straight after a navigation is meaningless. Waiting for
 * the request behind the grid to settle makes an absent row mean absent.
 */
export async function waitForGrid(page: Page) {
  await page.waitForLoadState("networkidle");
}

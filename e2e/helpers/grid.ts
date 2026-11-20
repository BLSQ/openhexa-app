import { Locator, Page } from "@playwright/test";

/**
 * The data grids render "No elements to display" while they are still loading,
 * so reading a row count straight after a navigation is meaningless. Waiting for
 * the requests behind the page to settle makes an absent row mean absent.
 *
 * Only for right after a navigation: Playwright reports the network as idle
 * once per document, so after that this returns at once whatever the page is
 * fetching. To wait for a search typed into a grid, use `searchGrid`.
 */
export async function waitForGrid(page: Page) {
  // eslint-disable-next-line playwright/no-networkidle -- the one place it is allowed, see above
  await page.waitForLoadState("networkidle");
}

/**
 * Types `text` into a grid's search box and waits for the filtered list, so
 * that a row missing afterwards is absent rather than not fetched yet. The
 * grids search on the server, with the text among the query's variables.
 */
export async function searchGrid(page: Page, input: Locator, text: string) {
  const term = JSON.stringify(text).slice(1, -1);
  const filtered = page.waitForResponse(
    (response) =>
      response.url().includes("/graphql") &&
      (response.request().postData() ?? "").includes(term),
  );
  await input.fill(text);
  await (await filtered).finished();
  // The response is in, but the rows are only drawn on the next render.
  await page.evaluate(
    () =>
      new Promise<void>((resolve) =>
        requestAnimationFrame(() => requestAnimationFrame(() => resolve())),
      ),
  );
}

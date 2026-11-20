import { Page } from "@playwright/test";

import { OUTSIDER_STORAGE_STATE } from "../config/environment";
import { test as base } from "./cleanup";

/**
 * Pages in browser contexts of their own, for checking what someone other than
 * the test account sees.
 *
 * `browser.newContext()` inherits the project's `use` options, storage state
 * included, so a context opened without one is still signed in as the test
 * account. The anonymous one is handed an explicitly empty state.
 */
export const test = base.extend<{ anonymousPage: Page; outsiderPage: Page }>({
  anonymousPage: async ({ browser }, use) => {
    const context = await browser.newContext({
      storageState: { cookies: [], origins: [] },
    });
    await use(await context.newPage());
    await context.close();
  },
  /** Signed in, but with no access to the test workspace. */
  outsiderPage: async ({ browser }, use) => {
    const context = await browser.newContext({
      storageState: OUTSIDER_STORAGE_STATE,
    });
    await use(await context.newPage());
    await context.close();
  },
});

export { expect } from "@playwright/test";
